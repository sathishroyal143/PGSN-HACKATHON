"""Constants for Communication module."""

# Conversation types
CONV_TYPE_BOOKING = 'booking'       # Between family and companion for a booking
CONV_TYPE_SUPPORT = 'support'       # Between user and support staff
CONV_TYPE_DIRECT = 'direct'         # General direct message

CONV_TYPE_CHOICES = [
    (CONV_TYPE_BOOKING, 'Booking Chat'),
    (CONV_TYPE_SUPPORT, 'Support Chat'),
    (CONV_TYPE_DIRECT, 'Direct Message'),
]

# Conversation status
CONV_STATUS_ACTIVE = 'active'
CONV_STATUS_CLOSED = 'closed'
CONV_STATUS_ARCHIVED = 'archived'

CONV_STATUS_CHOICES = [
    (CONV_STATUS_ACTIVE, 'Active'),
    (CONV_STATUS_CLOSED, 'Closed'),
    (CONV_STATUS_ARCHIVED, 'Archived'),
]

# Message types
MSG_TYPE_TEXT = 'text'
MSG_TYPE_IMAGE = 'image'
MSG_TYPE_FILE = 'file'
MSG_TYPE_LOCATION = 'location'
MSG_TYPE_SYSTEM = 'system'          # Auto-generated system messages

MSG_TYPE_CHOICES = [
    (MSG_TYPE_TEXT, 'Text'),
    (MSG_TYPE_IMAGE, 'Image'),
    (MSG_TYPE_FILE, 'File'),
    (MSG_TYPE_LOCATION, 'Location'),
    (MSG_TYPE_SYSTEM, 'System'),
]

# Message status
MSG_STATUS_SENT = 'sent'
MSG_STATUS_DELIVERED = 'delivered'
MSG_STATUS_READ = 'read'

MSG_STATUS_CHOICES = [
    (MSG_STATUS_SENT, 'Sent'),
    (MSG_STATUS_DELIVERED, 'Delivered'),
    (MSG_STATUS_READ, 'Read'),
]

# Call types
CALL_TYPE_AUDIO = 'audio'
CALL_TYPE_VIDEO = 'video'

CALL_TYPE_CHOICES = [
    (CALL_TYPE_AUDIO, 'Audio Call'),
    (CALL_TYPE_VIDEO, 'Video Call'),
]

# Call status
CALL_STATUS_INITIATED = 'initiated'
CALL_STATUS_RINGING = 'ringing'
CALL_STATUS_ANSWERED = 'answered'
CALL_STATUS_MISSED = 'missed'
CALL_STATUS_DECLINED = 'declined'
CALL_STATUS_ENDED = 'ended'
CALL_STATUS_FAILED = 'failed'

CALL_STATUS_CHOICES = [
    (CALL_STATUS_INITIATED, 'Initiated'),
    (CALL_STATUS_RINGING, 'Ringing'),
    (CALL_STATUS_ANSWERED, 'Answered'),
    (CALL_STATUS_MISSED, 'Missed'),
    (CALL_STATUS_DECLINED, 'Declined'),
    (CALL_STATUS_ENDED, 'Ended'),
    (CALL_STATUS_FAILED, 'Failed'),
]

# WebSocket message types
WS_TYPE_NEW_MESSAGE = 'new_message'
WS_TYPE_MESSAGE_READ = 'message_read'
WS_TYPE_TYPING = 'typing'
WS_TYPE_STOP_TYPING = 'stop_typing'
WS_TYPE_CALL_INITIATE = 'call_initiate'
WS_TYPE_CALL_ANSWER = 'call_answer'
WS_TYPE_CALL_DECLINE = 'call_decline'
WS_TYPE_CALL_END = 'call_end'
WS_TYPE_ERROR = 'error'

# Channel group prefix
CHAT_GROUP_PREFIX = 'chat_conversation_'

# Max message length
MAX_MESSAGE_LENGTH = 4000

# Max file size (bytes) — 10 MB
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
