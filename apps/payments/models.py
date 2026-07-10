"""Payments models — Payment, Invoice, Refund, Wallet, WalletTransaction."""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.bookings.models import Booking
from . import constants

User = get_user_model()


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking, on_delete=models.PROTECT,
        related_name='payments', db_index=True,
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='payments', db_index=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(
        max_length=25, choices=constants.PAYMENT_STATUS_CHOICES,
        default=constants.PAYMENT_STATUS_PENDING, db_index=True,
    )
    method = models.CharField(
        max_length=15, choices=constants.PAYMENT_METHOD_CHOICES,
        blank=True,
    )
    # Gateway fields
    gateway_order_id = models.CharField(max_length=255, blank=True, db_index=True)
    gateway_payment_id = models.CharField(max_length=255, blank=True, db_index=True)
    gateway_signature = models.CharField(max_length=512, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)

    paid_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking', 'status']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"Payment {self.id} — ₹{self.amount} [{self.status}]"


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(
        Booking, on_delete=models.PROTECT,
        related_name='invoice',
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='invoices', db_index=True,
    )
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    status = models.CharField(
        max_length=15, choices=constants.INVOICE_STATUS_CHOICES,
        default=constants.INVOICE_STATUS_DRAFT, db_index=True,
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    line_items = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.invoice_number} — ₹{self.total_amount} [{self.status}]"


class Refund(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(
        Payment, on_delete=models.PROTECT,
        related_name='refunds', db_index=True,
    )
    requested_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='refund_requests',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=15, choices=constants.REFUND_STATUS_CHOICES,
        default=constants.REFUND_STATUS_REQUESTED, db_index=True,
    )
    reason = models.TextField()
    gateway_refund_id = models.CharField(max_length=255, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'refunds'
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund {self.id} — ₹{self.amount} [{self.status}]"


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='wallet',
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallets'

    def __str__(self):
        return f"Wallet {self.user_id} — ₹{self.balance}"


class WalletTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE,
        related_name='transactions', db_index=True,
    )
    txn_type = models.CharField(max_length=10, choices=constants.WALLET_TXN_CHOICES, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    reference_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wallet_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', 'created_at']),
        ]

    def __str__(self):
        return f"WalletTxn {self.txn_type} ₹{self.amount} → balance ₹{self.balance_after}"
