"""Payments services."""
import logging
from .repositories import InvoiceRepository, PaymentRepository, RefundRepository, WalletRepository
from .exceptions import (
    PaymentNotFoundException, RefundNotFoundException,
    RefundNotAllowedException, PaymentAlreadyPaidException,
)
from . import constants

logger = logging.getLogger('carebridge')


class PaymentService:

    @staticmethod
    def initiate(booking_id, user_id, amount):
        """Create a pending payment record and return it (gateway order created separately)."""
        existing = PaymentRepository.get_for_booking(booking_id).filter(
            status=constants.PAYMENT_STATUS_SUCCESS
        ).first()
        if existing:
            raise PaymentAlreadyPaidException()
        return PaymentRepository.create(booking_id, user_id, amount)

    @staticmethod
    def verify_and_capture(payment_id, gateway_payment_id, gateway_signature, gateway_response, method):
        payment = PaymentRepository.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundException()

        # Verify Razorpay signature only when key is configured
        from django.conf import settings
        if settings.RAZORPAY_KEY_SECRET:
            try:
                import razorpay
                client = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                )
                client.utility.verify_payment_signature({
                    'razorpay_order_id': gateway_payment_id,
                    'razorpay_payment_id': gateway_payment_id,
                    'razorpay_signature': gateway_signature,
                })
            except Exception as exc:
                logger.warning('Razorpay signature verification failed: %s', exc)
                raise
        else:
            logger.warning(
                'RAZORPAY_KEY_SECRET not set — skipping signature verification (dev mode). '
                'payment=%s', payment_id
            )

        PaymentRepository.mark_success(
            payment_id, gateway_payment_id, gateway_signature, gateway_response, method,
        )
        InvoiceRepository.mark_paid(payment.booking_id)
        logger.info("Payment captured payment=%s booking=%s", payment_id, payment.booking_id)

    @staticmethod
    def fail(payment_id, reason=''):
        payment = PaymentRepository.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundException()
        PaymentRepository.mark_failed(payment_id, reason)


class RefundService:

    @staticmethod
    def request(payment_id, user_id, amount, reason):
        payment = PaymentRepository.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundException()
        if payment.status != constants.PAYMENT_STATUS_SUCCESS:
            raise RefundNotAllowedException()
        return RefundRepository.create(payment_id, user_id, amount, reason)

    @staticmethod
    def process(refund_id, gateway_refund_id=''):
        refund = RefundRepository.get_by_id(refund_id)
        if not refund:
            raise RefundNotFoundException()
        RefundRepository.process(refund_id, gateway_refund_id)
        # Credit wallet with refund amount
        WalletRepository.get_or_create(refund.requested_by_id)
        WalletRepository.credit(
            refund.requested_by_id, refund.amount,
            description='Refund credited', reference_id=str(refund_id),
        )
        logger.info("Refund processed refund=%s", refund_id)


class InvoiceService:

    @staticmethod
    def generate(booking_id, user_id, subtotal, tax_rate=0.18, discount=0, line_items=None, notes=''):
        tax_amount = round(subtotal * tax_rate, 2)
        return InvoiceRepository.create(
            booking_id=booking_id, user_id=user_id,
            subtotal=subtotal, tax_amount=tax_amount,
            discount_amount=discount,
            line_items=line_items or [],
            notes=notes,
        )
