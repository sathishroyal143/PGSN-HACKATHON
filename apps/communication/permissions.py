"""Communication permissions."""
from rest_framework.permissions import BasePermission
from .repositories import ParticipantRepository


class IsConversationParticipant(BasePermission):
    """Grants access only to participants of the conversation."""
    message = 'You are not a participant of this conversation.'

    def has_permission(self, request, view):
        conversation_id = view.kwargs.get('conversation_id')
        if not conversation_id:
            return False
        return ParticipantRepository.is_participant(conversation_id, request.user.id)
