"""Payments admin."""
from django.contrib import admin
from .models import Invoice, Payment, Refund, Wallet, WalletTransaction


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'booking', 'amount', 'currency', 'status', 'method', 'paid_at', 'created_at']
    list_filter = ['status', 'method', 'currency']
    search_fields = ['user__email', 'gateway_payment_id', 'gateway_order_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'user', 'booking', 'total_amount', 'status', 'issued_at']
    list_filter = ['status']
    search_fields = ['invoice_number', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'requested_by', 'amount', 'status', 'processed_at']
    list_filter = ['status']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'is_active', 'updated_at']
    search_fields = ['user__email']
    readonly_fields = ['id', 'created_at']


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'wallet', 'txn_type', 'amount', 'balance_after', 'created_at']
    list_filter = ['txn_type']
    readonly_fields = ['id', 'created_at']
