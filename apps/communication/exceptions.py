"""Communication custom exceptions."""
from common.exceptions import CareBridgeBaseException
from rest_framework import status


class ConversationNotFoundException(CareBridgeBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Conversation not found.'
    default_code = 'conversation_not_found'


class MessageNotFoundException(CareBridgeBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Message not found.'
    default_code = 'message_not_found'


class NotParticipantException(CareBridgeBaseException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You are not a participant of this conversation.'
    default_code = 'not_participant'


class ConversationClosedException(CareBridgeBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'This conversation is closed.'
    default_code = 'conversation_closed'


class CallNotFoundException(CareBridgeBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Call log not found.'
    default_code = 'call_not_found'
