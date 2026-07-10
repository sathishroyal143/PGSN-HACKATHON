"""Payments URL configuration."""
from django.urls import path
from .views import (
    InvoiceDetailView, InvoiceListView, PaymentListView,
    PaymentOrderView, PaymentVerifyView, PaymentWebhookView,
    RefundListView, RefundProcessView,
    WalletTransactionListView, WalletView,
)

app_name = 'payments'

urlpatterns = [
    path('', PaymentListView.as_view(), name='payment-list'),
    path('<uuid:payment_id>/order/', PaymentOrderView.as_view(), name='payment-order'),
    path('<uuid:payment_id>/verify/', PaymentVerifyView.as_view(), name='payment-verify'),
    path('<uuid:payment_id>/refunds/', RefundListView.as_view(), name='refund-list'),
    path('refunds/<uuid:refund_id>/process/', RefundProcessView.as_view(), name='refund-process'),
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'),
    path('invoices/booking/<uuid:booking_id>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('wallet/transactions/', WalletTransactionListView.as_view(), name='wallet-transactions'),
]
