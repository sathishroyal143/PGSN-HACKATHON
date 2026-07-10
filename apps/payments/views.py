"""Payments views."""
import hashlib
import hmac
import logging

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers as drf_serializers, status

from .selectors import InvoiceSelectors, PaymentSelectors, WalletSelectors
from .services import InvoiceService, PaymentService, RefundService
from .repositories import RefundRepository, PaymentRepository
from .serializers import (
    InitiatePaymentSerializer, InvoiceSerializer, PaymentSerializer,
    RefundSerializer, RequestRefundSerializer,
    VerifyPaymentSerializer, WalletSerializer, WalletTransactionSerializer,
)
from . import constants

logger = logging.getLogger('carebridge')

class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = PaymentSelectors.for_user(request.user.id)
        return Response({'data': PaymentSerializer(qs, many=True).data})

    def post(self, request):
        ser = InitiatePaymentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        payment = PaymentService.initiate(
            booking_id=ser.validated_data['booking_id'],
            user_id=request.user.id,
            amount=ser.validated_data['amount'],
        )
        return Response({'data': PaymentSerializer(payment).data}, status=status.HTTP_201_CREATED)


class PaymentOrderView(APIView):
    """Create a Razorpay order for a pending payment."""
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        payment = PaymentRepository.get_by_id(payment_id)
        if not payment:
            return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)
        if payment.user_id != request.user.id:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        if payment.status != constants.PAYMENT_STATUS_PENDING:
            return Response({'error': 'Payment is not in pending state.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.conf import settings
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            # Dev mode: return a mock order
            mock_order_id = f'order_dev_{payment_id!s:.8s}'
            PaymentRepository.set_gateway_order_id(payment_id, mock_order_id)
            return Response({
                'data': {
                    'order_id': mock_order_id,
                    'amount': int(payment.amount * 100),
                    'currency': payment.currency,
                    'key': 'rzp_test_dev',
                }
            })

        try:
            import razorpay
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            order = client.order.create({
                'amount': int(payment.amount * 100),
                'currency': payment.currency,
                'receipt': str(payment_id),
                'payment_capture': 1,
            })
            PaymentRepository.set_gateway_order_id(payment_id, order['id'])
            return Response({
                'data': {
                    'order_id': order['id'],
                    'amount': order['amount'],
                    'currency': order['currency'],
                    'key': settings.RAZORPAY_KEY_ID,
                }
            })
        except Exception as exc:
            logger.error('Razorpay order creation failed: %s', exc)
            return Response({'error': 'Payment gateway error.'}, status=status.HTTP_502_BAD_GATEWAY)


class PaymentVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        ser = VerifyPaymentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        PaymentService.verify_and_capture(
            payment_id=payment_id,
            gateway_payment_id=d['gateway_payment_id'],
            gateway_signature=d['gateway_signature'],
            gateway_response=d.get('gateway_response', {}),
            method=d.get('method', 'card'),
        )
        return Response({'message': 'Payment verified successfully.'})


class RefundListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        qs = RefundRepository.get_for_payment(payment_id)
        return Response({'data': RefundSerializer(qs, many=True).data})

    def post(self, request, payment_id):
        ser = RequestRefundSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        refund = RefundService.request(
            payment_id=payment_id,
            user_id=request.user.id,
            amount=ser.validated_data['amount'],
            reason=ser.validated_data['reason'],
        )
        return Response({'data': RefundSerializer(refund).data}, status=status.HTTP_201_CREATED)


class RefundProcessView(APIView):
    """Admin-only: process (approve and credit) a refund."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, refund_id):
        class _Ser(drf_serializers.Serializer):
            gateway_refund_id = drf_serializers.CharField(required=False, default='')

        ser = _Ser(data=request.data)
        ser.is_valid(raise_exception=True)
        refund = RefundRepository.get_by_id(refund_id)
        if not refund:
            return Response({'error': 'Refund not found.'}, status=status.HTTP_404_NOT_FOUND)
        if refund.status != constants.REFUND_STATUS_REQUESTED:
            return Response({'error': 'Refund is not in requested state.'}, status=status.HTTP_400_BAD_REQUEST)
        RefundService.process(refund_id, ser.validated_data['gateway_refund_id'])
        refund.refresh_from_db()
        return Response({'data': RefundSerializer(refund).data})


class PaymentWebhookView(APIView):
    """Razorpay webhook endpoint — no auth, verified by signature."""
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        from django.conf import settings
        webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')
        if webhook_secret:
            sig = request.headers.get('X-Razorpay-Signature', '')
            body = request.body
            expected = hmac.new(
                webhook_secret.encode(), body, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(expected, sig):
                return Response({'error': 'Invalid signature.'}, status=status.HTTP_400_BAD_REQUEST)

        event = request.data.get('event', '')
        payload = request.data.get('payload', {})

        if event == 'payment.captured':
            payment_entity = payload.get('payment', {}).get('entity', {})
            order_id = payment_entity.get('order_id', '')
            payment_id_gw = payment_entity.get('id', '')
            if order_id:
                payment = PaymentRepository.get_by_gateway_order_id(order_id)
                if payment and payment.status == constants.PAYMENT_STATUS_PENDING:
                    PaymentService.verify_and_capture(
                        payment_id=payment.id,
                        gateway_payment_id=payment_id_gw,
                        gateway_signature='webhook',
                        gateway_response=payment_entity,
                        method=payment_entity.get('method', 'card'),
                    )
        elif event == 'payment.failed':
            payment_entity = payload.get('payment', {}).get('entity', {})
            order_id = payment_entity.get('order_id', '')
            if order_id:
                payment = PaymentRepository.get_by_gateway_order_id(order_id)
                if payment:
                    PaymentService.fail(payment.id, payment_entity.get('error_description', ''))

        return Response({'status': 'ok'})


class InvoiceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = InvoiceSelectors.for_user(request.user.id)
        return Response({'data': InvoiceSerializer(qs, many=True).data})


class InvoiceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        invoice = InvoiceSelectors.for_booking(booking_id)
        if not invoice:
            return Response({'error': 'Invoice not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'data': InvoiceSerializer(invoice).data})


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = WalletSelectors.get(request.user.id)
        return Response({'data': WalletSerializer(wallet).data})


class WalletTransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = WalletSelectors.transactions(request.user.id)
        return Response({'data': WalletTransactionSerializer(qs, many=True).data})
