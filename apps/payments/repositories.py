"""Payments repositories."""
from django.utils import timezone
from django.db import transaction as db_transaction
from .models import Invoice, Payment, Refund, Wallet, WalletTransaction
from . import constants


class PaymentRepository:

    @staticmethod
    def create(booking_id, user_id, amount, currency='INR'):
        return Payment.objects.create(
            booking_id=booking_id, user_id=user_id,
            amount=amount, currency=currency,
        )

    @staticmethod
    def get_by_id(payment_id):
        return Payment.objects.filter(id=payment_id).first()

    @staticmethod
    def get_for_booking(booking_id):
        return Payment.objects.filter(booking_id=booking_id).order_by('-created_at')

    @staticmethod
    def get_for_user(user_id):
        return Payment.objects.filter(user_id=user_id).order_by('-created_at')

    @staticmethod
    def mark_success(payment_id, gateway_payment_id, gateway_signature, gateway_response, method):
        Payment.objects.filter(id=payment_id).update(
            status=constants.PAYMENT_STATUS_SUCCESS,
            gateway_payment_id=gateway_payment_id,
            gateway_signature=gateway_signature,
            gateway_response=gateway_response,
            method=method,
            paid_at=timezone.now(),
        )

    @staticmethod
    def mark_failed(payment_id, reason=''):
        Payment.objects.filter(id=payment_id).update(
            status=constants.PAYMENT_STATUS_FAILED,
            failure_reason=reason,
        )

    @staticmethod
    def set_gateway_order_id(payment_id, gateway_order_id):
        Payment.objects.filter(id=payment_id).update(gateway_order_id=gateway_order_id)

    @staticmethod
    def get_by_gateway_order_id(gateway_order_id):
        return Payment.objects.filter(gateway_order_id=gateway_order_id).first()


class InvoiceRepository:

    @staticmethod
    def create(booking_id, user_id, subtotal, tax_amount, discount_amount, line_items, notes=''):
        total = subtotal + tax_amount - discount_amount
        number = f"INV-{booking_id!s:.8s}-{timezone.now().strftime('%Y%m%d')}"
        return Invoice.objects.create(
            booking_id=booking_id, user_id=user_id,
            invoice_number=number,
            subtotal=subtotal, tax_amount=tax_amount,
            discount_amount=discount_amount, total_amount=total,
            line_items=line_items, notes=notes,
            status=constants.INVOICE_STATUS_ISSUED,
            issued_at=timezone.now(),
        )

    @staticmethod
    def get_by_id(invoice_id):
        return Invoice.objects.filter(id=invoice_id).first()

    @staticmethod
    def get_for_booking(booking_id):
        return Invoice.objects.filter(booking_id=booking_id).first()

    @staticmethod
    def get_for_user(user_id):
        return Invoice.objects.filter(user_id=user_id).order_by('-created_at')

    @staticmethod
    def mark_paid(booking_id):
        Invoice.objects.filter(booking_id=booking_id).update(status=constants.INVOICE_STATUS_PAID)


class RefundRepository:

    @staticmethod
    def create(payment_id, requested_by_id, amount, reason):
        return Refund.objects.create(
            payment_id=payment_id,
            requested_by_id=requested_by_id,
            amount=amount, reason=reason,
        )

    @staticmethod
    def get_by_id(refund_id):
        return Refund.objects.filter(id=refund_id).first()

    @staticmethod
    def get_for_payment(payment_id):
        return Refund.objects.filter(payment_id=payment_id)

    @staticmethod
    def process(refund_id, gateway_refund_id=''):
        Refund.objects.filter(id=refund_id).update(
            status=constants.REFUND_STATUS_PROCESSED,
            gateway_refund_id=gateway_refund_id,
            processed_at=timezone.now(),
        )


class WalletRepository:

    @staticmethod
    def get_or_create(user_id):
        wallet, _ = Wallet.objects.get_or_create(user_id=user_id)
        return wallet

    @staticmethod
    @db_transaction.atomic
    def credit(user_id, amount, description='', reference_id=''):
        wallet = Wallet.objects.select_for_update().get(user_id=user_id)
        wallet.balance += amount
        wallet.save(update_fields=['balance', 'updated_at'])
        WalletTransaction.objects.create(
            wallet=wallet, txn_type=constants.WALLET_CREDIT,
            amount=amount, balance_after=wallet.balance,
            description=description, reference_id=reference_id,
        )
        return wallet

    @staticmethod
    @db_transaction.atomic
    def debit(user_id, amount, description='', reference_id=''):
        from .exceptions import InsufficientWalletBalanceException
        wallet = Wallet.objects.select_for_update().get(user_id=user_id)
        if wallet.balance < amount:
            raise InsufficientWalletBalanceException()
        wallet.balance -= amount
        wallet.save(update_fields=['balance', 'updated_at'])
        WalletTransaction.objects.create(
            wallet=wallet, txn_type=constants.WALLET_DEBIT,
            amount=amount, balance_after=wallet.balance,
            description=description, reference_id=reference_id,
        )
        return wallet

    @staticmethod
    def get_transactions(user_id):
        wallet = Wallet.objects.filter(user_id=user_id).first()
        if not wallet:
            return WalletTransaction.objects.none()
        return wallet.transactions.order_by('-created_at')
