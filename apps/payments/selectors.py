"""Payments selectors."""
from .repositories import InvoiceRepository, PaymentRepository, RefundRepository, WalletRepository


class PaymentSelectors:

    @staticmethod
    def for_user(user_id):
        return PaymentRepository.get_for_user(user_id)

    @staticmethod
    def for_booking(booking_id):
        return PaymentRepository.get_for_booking(booking_id)


class InvoiceSelectors:

    @staticmethod
    def for_user(user_id):
        return InvoiceRepository.get_for_user(user_id)

    @staticmethod
    def for_booking(booking_id):
        return InvoiceRepository.get_for_booking(booking_id)


class WalletSelectors:

    @staticmethod
    def get(user_id):
        return WalletRepository.get_or_create(user_id)

    @staticmethod
    def transactions(user_id):
        return WalletRepository.get_transactions(user_id)
