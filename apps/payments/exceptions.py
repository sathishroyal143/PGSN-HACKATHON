"""Payments exceptions."""
from rest_framework.exceptions import APIException, NotFound
from rest_framework import status


class PaymentNotFoundException(NotFound):
    default_detail = 'Payment not found.'


class InvoiceNotFoundException(NotFound):
    default_detail = 'Invoice not found.'


class RefundNotFoundException(NotFound):
    default_detail = 'Refund not found.'


class PaymentAlreadyPaidException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'This booking has already been paid.'


class InsufficientWalletBalanceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Insufficient wallet balance.'


class RefundNotAllowedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Refund is not allowed for this payment.'
