"""Constants for Payments module."""

# Payment status
PAYMENT_STATUS_PENDING = 'pending'
PAYMENT_STATUS_PROCESSING = 'processing'
PAYMENT_STATUS_SUCCESS = 'success'
PAYMENT_STATUS_FAILED = 'failed'
PAYMENT_STATUS_REFUNDED = 'refunded'
PAYMENT_STATUS_PARTIALLY_REFUNDED = 'partially_refunded'
PAYMENT_STATUS_CANCELLED = 'cancelled'

PAYMENT_STATUS_CHOICES = [
    (PAYMENT_STATUS_PENDING, 'Pending'),
    (PAYMENT_STATUS_PROCESSING, 'Processing'),
    (PAYMENT_STATUS_SUCCESS, 'Success'),
    (PAYMENT_STATUS_FAILED, 'Failed'),
    (PAYMENT_STATUS_REFUNDED, 'Refunded'),
    (PAYMENT_STATUS_PARTIALLY_REFUNDED, 'Partially Refunded'),
    (PAYMENT_STATUS_CANCELLED, 'Cancelled'),
]

# Payment method
METHOD_CARD = 'card'
METHOD_UPI = 'upi'
METHOD_NETBANKING = 'netbanking'
METHOD_WALLET = 'wallet'
METHOD_CASH = 'cash'

PAYMENT_METHOD_CHOICES = [
    (METHOD_CARD, 'Card'),
    (METHOD_UPI, 'UPI'),
    (METHOD_NETBANKING, 'Net Banking'),
    (METHOD_WALLET, 'Wallet'),
    (METHOD_CASH, 'Cash'),
]

# Invoice status
INVOICE_STATUS_DRAFT = 'draft'
INVOICE_STATUS_ISSUED = 'issued'
INVOICE_STATUS_PAID = 'paid'
INVOICE_STATUS_OVERDUE = 'overdue'
INVOICE_STATUS_CANCELLED = 'cancelled'

INVOICE_STATUS_CHOICES = [
    (INVOICE_STATUS_DRAFT, 'Draft'),
    (INVOICE_STATUS_ISSUED, 'Issued'),
    (INVOICE_STATUS_PAID, 'Paid'),
    (INVOICE_STATUS_OVERDUE, 'Overdue'),
    (INVOICE_STATUS_CANCELLED, 'Cancelled'),
]

# Refund status
REFUND_STATUS_REQUESTED = 'requested'
REFUND_STATUS_APPROVED = 'approved'
REFUND_STATUS_PROCESSED = 'processed'
REFUND_STATUS_REJECTED = 'rejected'

REFUND_STATUS_CHOICES = [
    (REFUND_STATUS_REQUESTED, 'Requested'),
    (REFUND_STATUS_APPROVED, 'Approved'),
    (REFUND_STATUS_PROCESSED, 'Processed'),
    (REFUND_STATUS_REJECTED, 'Rejected'),
]

# Wallet transaction types
WALLET_CREDIT = 'credit'
WALLET_DEBIT = 'debit'

WALLET_TXN_CHOICES = [
    (WALLET_CREDIT, 'Credit'),
    (WALLET_DEBIT, 'Debit'),
]
