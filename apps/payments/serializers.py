"""Payments serializers."""
from rest_framework import serializers
from .models import Invoice, Payment, Refund, Wallet, WalletTransaction


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'amount', 'currency', 'status', 'method',
            'gateway_order_id', 'gateway_payment_id', 'paid_at',
            'failure_reason', 'created_at',
        ]
        read_only_fields = fields


class InitiatePaymentSerializer(serializers.Serializer):
    booking_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class VerifyPaymentSerializer(serializers.Serializer):
    gateway_payment_id = serializers.CharField()
    gateway_signature = serializers.CharField()
    method = serializers.CharField(default='card')
    gateway_response = serializers.JSONField(default=dict)


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id', 'booking', 'invoice_number', 'status',
            'subtotal', 'tax_amount', 'discount_amount', 'total_amount',
            'line_items', 'notes', 'issued_at', 'due_date', 'created_at',
        ]
        read_only_fields = fields


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = [
            'id', 'payment', 'amount', 'status', 'reason',
            'gateway_refund_id', 'processed_at', 'created_at',
        ]
        read_only_fields = fields


class RequestRefundSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField()


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'is_active', 'updated_at']
        read_only_fields = fields


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'txn_type', 'amount', 'balance_after', 'description', 'reference_id', 'created_at']
        read_only_fields = fields
