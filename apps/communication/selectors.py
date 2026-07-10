"""Communication selectors — read-only query helpers."""
from .models import Conversation, Message, CallLog
from .repositories import ConversationRepository, MessageRepository, CallLogRepository, ParticipantRepository


class ConversationSelectors:

    @staticmethod
    def get_user_conversations(user_id):
        return ConversationRepository.get_for_user(user_id)

    @staticmethod
    def get_conversation(conversation_id, user_id) -> Conversation | None:
        if not ParticipantRepository.is_participant(conversation_id, user_id):
            return None
        return ConversationRepository.get_by_id(conversation_id)

    @staticmethod
    def get_unread_count(conversation_id, user_id) -> int:
        participant = ParticipantRepository.get(conversation_id, user_id)
        return participant.unread_count if participant else 0


class MessageSelectors:

    @staticmethod
    def get_messages(conversation_id, before_id=None, limit: int = 50) -> list:
        return MessageRepository.get_for_conversation(conversation_id, before_id, limit)

    @staticmethod
    def get_message(message_id) -> Message | None:
        return MessageRepository.get_by_id(message_id)


class CallSelectors:

    @staticmethod
    def get_call_history(conversation_id):
        return CallLogRepository.get_for_conversation(conversation_id)

    @staticmethod
    def get_call(call_id) -> CallLog | None:
        return CallLogRepository.get_by_id(call_id)
