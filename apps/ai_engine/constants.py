"""Constants for AI Engine module."""

# Request types
REQUEST_TYPE_COMPANION_MATCH = 'companion_match'
REQUEST_TYPE_MEDICAL_SUMMARY = 'medical_summary'
REQUEST_TYPE_TRUST_SCORE = 'trust_score'
REQUEST_TYPE_PRIORITY = 'priority'
REQUEST_TYPE_REMINDER = 'reminder'
REQUEST_TYPE_CHAT = 'chat'

REQUEST_TYPE_CHOICES = [
    (REQUEST_TYPE_COMPANION_MATCH, 'Companion Match'),
    (REQUEST_TYPE_MEDICAL_SUMMARY, 'Medical Summary'),
    (REQUEST_TYPE_TRUST_SCORE, 'Trust Score'),
    (REQUEST_TYPE_PRIORITY, 'Priority Assessment'),
    (REQUEST_TYPE_REMINDER, 'Care Reminder'),
    (REQUEST_TYPE_CHAT, 'AI Chat'),
]

# Request status
STATUS_PENDING = 'pending'
STATUS_PROCESSING = 'processing'
STATUS_COMPLETED = 'completed'
STATUS_FAILED = 'failed'

STATUS_CHOICES = [
    (STATUS_PENDING, 'Pending'),
    (STATUS_PROCESSING, 'Processing'),
    (STATUS_COMPLETED, 'Completed'),
    (STATUS_FAILED, 'Failed'),
]

# Match score weights
WEIGHT_RATING = 0.30
WEIGHT_SKILLS = 0.25
WEIGHT_EXPERIENCE = 0.15
WEIGHT_TRUST_SCORE = 0.20
WEIGHT_AVAILABILITY = 0.10

# Priority levels
PRIORITY_LOW = 'low'
PRIORITY_MEDIUM = 'medium'
PRIORITY_HIGH = 'high'
PRIORITY_EMERGENCY = 'emergency'

PRIORITY_CHOICES = [
    (PRIORITY_LOW, 'Low'),
    (PRIORITY_MEDIUM, 'Medium'),
    (PRIORITY_HIGH, 'High'),
    (PRIORITY_EMERGENCY, 'Emergency'),
]
