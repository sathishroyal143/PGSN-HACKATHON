"""Constants for the Analytics module."""

EVENT_USER_REGISTERED = 'user_registered'
EVENT_BOOKING_CREATED = 'booking_created'
EVENT_BOOKING_COMPLETED = 'booking_completed'
EVENT_PAYMENT_COMPLETED = 'payment_completed'
EVENT_API_REQUEST = 'api_request'
EVENT_CUSTOM = 'custom'

EVENT_TYPE_CHOICES = [
    (EVENT_USER_REGISTERED, 'User Registered'),
    (EVENT_BOOKING_CREATED, 'Booking Created'),
    (EVENT_BOOKING_COMPLETED, 'Booking Completed'),
    (EVENT_PAYMENT_COMPLETED, 'Payment Completed'),
    (EVENT_API_REQUEST, 'API Request'),
    (EVENT_CUSTOM, 'Custom'),
]

REPORT_BOOKINGS = 'bookings'
REPORT_REVENUE = 'revenue'
REPORT_USER_GROWTH = 'user_growth'
REPORT_COMPANION_PERFORMANCE = 'companion_performance'

REPORT_TYPE_CHOICES = [
    (REPORT_BOOKINGS, 'Bookings'),
    (REPORT_REVENUE, 'Revenue'),
    (REPORT_USER_GROWTH, 'User Growth'),
    (REPORT_COMPANION_PERFORMANCE, 'Companion Performance'),
]

REPORT_PENDING = 'pending'
REPORT_PROCESSING = 'processing'
REPORT_COMPLETED = 'completed'
REPORT_FAILED = 'failed'

REPORT_STATUS_CHOICES = [
    (REPORT_PENDING, 'Pending'),
    (REPORT_PROCESSING, 'Processing'),
    (REPORT_COMPLETED, 'Completed'),
    (REPORT_FAILED, 'Failed'),
]

INSIGHT_OPERATIONS = 'operations'
INSIGHT_REVENUE = 'revenue'
INSIGHT_USERS = 'users'
INSIGHT_QUALITY = 'quality'

INSIGHT_CATEGORY_CHOICES = [
    (INSIGHT_OPERATIONS, 'Operations'),
    (INSIGHT_REVENUE, 'Revenue'),
    (INSIGHT_USERS, 'Users'),
    (INSIGHT_QUALITY, 'Quality'),
]

SEVERITY_INFO = 'info'
SEVERITY_WARNING = 'warning'
SEVERITY_CRITICAL = 'critical'

INSIGHT_SEVERITY_CHOICES = [
    (SEVERITY_INFO, 'Info'),
    (SEVERITY_WARNING, 'Warning'),
    (SEVERITY_CRITICAL, 'Critical'),
]
