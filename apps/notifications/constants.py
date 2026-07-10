"""Constants for Notifications module."""

# Notification types
NOTIF_TYPE_BOOKING_CONFIRMED = 'booking_confirmed'
NOTIF_TYPE_BOOKING_CANCELLED = 'booking_cancelled'
NOTIF_TYPE_BOOKING_COMPLETED = 'booking_completed'
NOTIF_TYPE_COMPANION_ASSIGNED = 'companion_assigned'
NOTIF_TYPE_COMPANION_ARRIVED = 'companion_arrived'
NOTIF_TYPE_MESSAGE_RECEIVED = 'message_received'
NOTIF_TYPE_PAYMENT_SUCCESS = 'payment_success'
NOTIF_TYPE_PAYMENT_FAILED = 'payment_failed'
NOTIF_TYPE_REVIEW_RECEIVED = 'review_received'
NOTIF_TYPE_SYSTEM = 'system'
NOTIF_TYPE_REMINDER = 'reminder'
TYPE_JOURNEY_UPDATE = 'journey_update'

NOTIF_TYPE_CHOICES = [
    (NOTIF_TYPE_BOOKING_CONFIRMED, 'Booking Confirmed'),
    (NOTIF_TYPE_BOOKING_CANCELLED, 'Booking Cancelled'),
    (NOTIF_TYPE_BOOKING_COMPLETED, 'Booking Completed'),
    (NOTIF_TYPE_COMPANION_ASSIGNED, 'Companion Assigned'),
    (NOTIF_TYPE_COMPANION_ARRIVED, 'Companion Arrived'),
    (NOTIF_TYPE_MESSAGE_RECEIVED, 'Message Received'),
    (NOTIF_TYPE_PAYMENT_SUCCESS, 'Payment Success'),
    (NOTIF_TYPE_PAYMENT_FAILED, 'Payment Failed'),
    (NOTIF_TYPE_REVIEW_RECEIVED, 'Review Received'),
    (NOTIF_TYPE_SYSTEM, 'System'),
    (NOTIF_TYPE_REMINDER, 'Reminder'),
    (TYPE_JOURNEY_UPDATE, 'Journey Update'),
]

# Delivery channels
CHANNEL_IN_APP = 'in_app'
CHANNEL_EMAIL = 'email'
CHANNEL_SMS = 'sms'
CHANNEL_PUSH = 'push'

CHANNEL_CHOICES = [
    (CHANNEL_IN_APP, 'In-App'),
    (CHANNEL_EMAIL, 'Email'),
    (CHANNEL_SMS, 'SMS'),
    (CHANNEL_PUSH, 'Push'),
]

# Priority
PRIORITY_LOW = 'low'
PRIORITY_NORMAL = 'normal'
PRIORITY_HIGH = 'high'

PRIORITY_CHOICES = [
    (PRIORITY_LOW, 'Low'),
    (PRIORITY_NORMAL, 'Normal'),
    (PRIORITY_HIGH, 'High'),
]
