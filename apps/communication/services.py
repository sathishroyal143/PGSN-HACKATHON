"""Communication services — business logic layer."""
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from apps.bookings.models import Booking
from .exceptions import ConversationClosedException, NotParticipantException
from .models import Conversation, Message, CallLog
from .repositories import (
    CallLogRepository, ConversationRepository, MessageRepository,
    ParticipantRepository, ReadReceiptRepository,
)
from . import constants

logger = logging.getLogger('carebridge')


def _chat_group(conversation_id: str) -> str:
    return f"{constants.CHAT_GROUP_PREFIX}{conversation_id}"


def _broadcast(conversation_id: str, message_type: str, payload: dict):
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            _chat_group(str(conversation_id)),
            {'type': 'chat.message', 'message_type': message_type, 'payload': payload},
        )
    except Exception as exc:
        logger.warning("Chat broadcast failed for conversation %s: %s", conversation_id, exc)


class ConversationService:

    @staticmethod
    def get_or_create_booking_conversation(booking: Booking) -> Conversation:
        """
        Idempotent — returns existing conversation or creates one.
        Adds family user and companion as participants.
        """
        existing = ConversationRepository.get_by_booking(booking.id)
        if existing:
            ParticipantRepository.add(existing, booking.family_user)
            if booking.companion:
                ParticipantRepository.add(existing, booking.companion)
            return existing

        title = f"Booking #{str(booking.id)[:8]} — {booking.patient.get_full_name()}"
        conversation = ConversationRepository.create({
            'conversation_type': constants.CONV_TYPE_BOOKING,
            'booking': booking,
            'title': title,
            'status': constants.CONV_STATUS_ACTIVE,
        })
        ParticipantRepository.add(conversation, booking.family_user)
        if booking.companion:
            ParticipantRepository.add(conversation, booking.companion)

        logger.info("Created booking conversation %s for booking %s", conversation.id, booking.id)
        return conversation

    @staticmethod
    def create_direct_conversation(initiator, recipient) -> Conversation:
        """Create a direct conversation between two users."""
        conversation = ConversationRepository.create({
            'conversation_type': constants.CONV_TYPE_DIRECT,
            'title': f"{initiator.get_full_name()} & {recipient.get_full_name()}",
        })
        ParticipantRepository.add(conversation, initiator)
        ParticipantRepository.add(conversation, recipient)
        return conversation

    @staticmethod
    def close_conversation(conversation: Conversation, user) -> Conversation:
        _assert_participant(conversation.id, user.id)
        return ConversationRepository.close(conversation)


class MessageService:

    @staticmethod
    def send_message(conversation: Conversation, sender, data: dict) -> Message:
        _assert_participant(conversation.id, sender.id)

        if conversation.status == constants.CONV_STATUS_CLOSED:
            raise ConversationClosedException()

        message = MessageRepository.create(conversation, sender, data)

        # Update conversation timestamp
        ConversationRepository.update_last_message_at(conversation)

        # Increment unread for all other participants
        ParticipantRepository.increment_unread(conversation.id, exclude_user_id=sender.id)

        # Broadcast to WebSocket group
        _broadcast(conversation.id, constants.WS_TYPE_NEW_MESSAGE, {
            'id': str(message.id),
            'conversation': str(conversation.id),
            'sender': sender.id,
            'sender_name': sender.get_full_name(),
            'message_type': message.message_type,
            'content': message.content,
            'file_url': message.file_url,
            'latitude': float(message.latitude) if message.latitude else None,
            'longitude': float(message.longitude) if message.longitude else None,
            'reply_to': str(message.reply_to_id) if message.reply_to_id else None,
            'created_at': message.created_at.isoformat(),
        })

        logger.info("Message %s sent in conversation %s", message.id, conversation.id)
        return message

    @staticmethod
    def mark_conversation_read(conversation: Conversation, user):
        _assert_participant(conversation.id, user.id)
        ReadReceiptRepository.bulk_mark_read(conversation.id, user)
        ParticipantRepository.reset_unread(conversation.id, user.id)

        _broadcast(conversation.id, constants.WS_TYPE_MESSAGE_READ, {
            'conversation_id': str(conversation.id),
            'user_id': str(user.id),
            'read_at': timezone.now().isoformat(),
        })

    @staticmethod
    def delete_message(message: Message, user) -> Message:
        if message.sender_id != user.id:
            raise NotParticipantException('You can only delete your own messages.')
        return MessageRepository.soft_delete(message)

    @staticmethod
    def broadcast_typing(conversation_id: str, user, is_typing: bool):
        msg_type = constants.WS_TYPE_TYPING if is_typing else constants.WS_TYPE_STOP_TYPING
        _broadcast(conversation_id, msg_type, {
            'conversation_id': conversation_id,
            'user_id': str(user.id),
            'user_name': user.get_full_name(),
        })


class CallService:

    @staticmethod
    def initiate_call(conversation: Conversation, caller, receiver, call_type: str) -> CallLog:
        _assert_participant(conversation.id, caller.id)
        call = CallLogRepository.create(conversation, caller, receiver, call_type)

        _broadcast(conversation.id, constants.WS_TYPE_CALL_INITIATE, {
            'call_id': str(call.id),
            'conversation_id': str(conversation.id),
            'caller_id': str(caller.id),
            'caller_name': caller.get_full_name(),
            'call_type': call_type,
        })
        return call

    @staticmethod
    def answer_call(call: CallLog, user) -> CallLog:
        call = CallLogRepository.update_status(call, constants.CALL_STATUS_ANSWERED)
        _broadcast(call.conversation_id, constants.WS_TYPE_CALL_ANSWER, {
            'call_id': str(call.id),
            'answered_by': str(user.id),
        })
        return call

    @staticmethod
    def decline_call(call: CallLog, user) -> CallLog:
        call = CallLogRepository.update_status(call, constants.CALL_STATUS_DECLINED)
        _broadcast(call.conversation_id, constants.WS_TYPE_CALL_DECLINE, {
            'call_id': str(call.id),
            'declined_by': str(user.id),
        })
        return call

    @staticmethod
    def end_call(call: CallLog, user) -> CallLog:
        call = CallLogRepository.update_status(call, constants.CALL_STATUS_ENDED)
        _broadcast(call.conversation_id, constants.WS_TYPE_CALL_END, {
            'call_id': str(call.id),
            'ended_by': str(user.id),
            'duration_seconds': call.duration_seconds,
        })
        return call


def _assert_participant(conversation_id, user_id):
    if not ParticipantRepository.is_participant(conversation_id, user_id):
        raise NotParticipantException()
