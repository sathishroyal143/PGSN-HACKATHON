"""Communication repositories — all database queries."""
import logging
from django.db.models import F as models_F, Q
from django.utils import timezone
from .models import Conversation, ConversationParticipant, Message, MessageReadReceipt, CallLog
from . import constants

logger = logging.getLogger('carebridge')


class ConversationRepository:

    @staticmethod
    def create(data: dict) -> Conversation:
        return Conversation.objects.create(**data)

    @staticmethod
    def get_by_id(conversation_id) -> Conversation | None:
        return Conversation.objects.filter(id=conversation_id, is_deleted=False).first()

    @staticmethod
    def get_by_booking(booking_id) -> Conversation | None:
        return Conversation.objects.filter(booking_id=booking_id, is_deleted=False).first()

    @staticmethod
    def get_for_user(user_id):
        """Return all active conversations the user participates in."""
        return (
            Conversation.objects
            .filter(
                participants__user_id=user_id,
                participants__is_active=True,
                is_deleted=False,
            )
            .select_related('booking')
            .prefetch_related('participants__user')
            .order_by('-last_message_at')
        )

    @staticmethod
    def update_last_message_at(conversation: Conversation):
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=['last_message_at', 'updated_at'])

    @staticmethod
    def close(conversation: Conversation) -> Conversation:
        conversation.status = constants.CONV_STATUS_CLOSED
        conversation.save(update_fields=['status', 'updated_at'])
        return conversation


class ParticipantRepository:

    @staticmethod
    def add(conversation: Conversation, user) -> ConversationParticipant:
        participant, _ = ConversationParticipant.objects.get_or_create(
            conversation=conversation,
            user=user,
            defaults={'is_active': True},
        )
        return participant

    @staticmethod
    def get(conversation_id, user_id) -> ConversationParticipant | None:
        return ConversationParticipant.objects.filter(
            conversation_id=conversation_id,
            user_id=user_id,
            is_active=True,
        ).first()

    @staticmethod
    def is_participant(conversation_id, user_id) -> bool:
        return ConversationParticipant.objects.filter(
            conversation_id=conversation_id,
            user_id=user_id,
            is_active=True,
        ).exists()

    @staticmethod
    def increment_unread(conversation_id, exclude_user_id):
        ConversationParticipant.objects.filter(
            conversation_id=conversation_id,
            is_active=True,
        ).exclude(user_id=exclude_user_id).update(
            unread_count=models_F('unread_count') + 1
        )

    @staticmethod
    def reset_unread(conversation_id, user_id):
        ConversationParticipant.objects.filter(
            conversation_id=conversation_id,
            user_id=user_id,
        ).update(unread_count=0, last_read_at=timezone.now())


class MessageRepository:

    @staticmethod
    def create(conversation: Conversation, sender, data: dict) -> Message:
        return Message.objects.create(
            conversation=conversation,
            sender=sender,
            **data,
        )

    @staticmethod
    def get_by_id(message_id) -> Message | None:
        return Message.objects.filter(id=message_id, is_deleted=False).first()

    @staticmethod
    def get_for_conversation(conversation_id, before_id=None, limit: int = 50):
        qs = Message.objects.filter(
            conversation_id=conversation_id,
            is_deleted=False,
        ).select_related('sender', 'reply_to__sender').order_by('-created_at')

        if before_id:
            anchor = Message.objects.filter(id=before_id).values('created_at').first()
            if anchor:
                qs = qs.filter(created_at__lt=anchor['created_at'])

        return list(reversed(qs[:limit]))

    @staticmethod
    def soft_delete(message: Message) -> Message:
        message.is_deleted = True
        message.deleted_at = timezone.now()
        message.content = ''
        message.save(update_fields=['is_deleted', 'deleted_at', 'content', 'updated_at'])
        return message

    @staticmethod
    def mark_delivered(conversation_id, exclude_sender_id):
        Message.objects.filter(
            conversation_id=conversation_id,
            status=constants.MSG_STATUS_SENT,
        ).exclude(sender_id=exclude_sender_id).update(status=constants.MSG_STATUS_DELIVERED)


class ReadReceiptRepository:

    @staticmethod
    def mark_read(message: Message, user) -> MessageReadReceipt:
        receipt, _ = MessageReadReceipt.objects.get_or_create(
            message=message, user=user,
        )
        return receipt

    @staticmethod
    def bulk_mark_read(conversation_id, user):
        unread = Message.objects.filter(
            conversation_id=conversation_id,
            is_deleted=False,
        ).exclude(sender=user)

        receipts = [
            MessageReadReceipt(message=msg, user=user)
            for msg in unread
            if not MessageReadReceipt.objects.filter(message=msg, user=user).exists()
        ]
        if receipts:
            MessageReadReceipt.objects.bulk_create(receipts, ignore_conflicts=True)

        Message.objects.filter(
            conversation_id=conversation_id,
            status__in=[constants.MSG_STATUS_SENT, constants.MSG_STATUS_DELIVERED],
        ).exclude(sender=user).update(status=constants.MSG_STATUS_READ)


class CallLogRepository:

    @staticmethod
    def create(conversation: Conversation, caller, receiver, call_type: str) -> CallLog:
        return CallLog.objects.create(
            conversation=conversation,
            caller=caller,
            receiver=receiver,
            call_type=call_type,
            status=constants.CALL_STATUS_INITIATED,
            started_at=timezone.now(),
        )

    @staticmethod
    def get_by_id(call_id) -> CallLog | None:
        return CallLog.objects.filter(id=call_id).first()

    @staticmethod
    def get_for_conversation(conversation_id):
        return CallLog.objects.filter(conversation_id=conversation_id).order_by('-created_at')

    @staticmethod
    def update_status(call: CallLog, status: str) -> CallLog:
        call.status = status
        if status == constants.CALL_STATUS_ANSWERED:
            call.answered_at = timezone.now()
        elif status in (constants.CALL_STATUS_ENDED, constants.CALL_STATUS_MISSED,
                        constants.CALL_STATUS_DECLINED, constants.CALL_STATUS_FAILED):
            call.ended_at = timezone.now()
            if call.answered_at:
                delta = call.ended_at - call.answered_at
                call.duration_seconds = int(delta.total_seconds())
        call.save()
        return call
