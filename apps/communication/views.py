"""Communication views — thin REST layer."""
import logging

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.exceptions import ResourceNotFoundException
from common.responses import created_response, deleted_response, success_response

from .exceptions import CallNotFoundException, ConversationNotFoundException, MessageNotFoundException
from .permissions import IsConversationParticipant
from .repositories import CallLogRepository, ConversationRepository, MessageRepository
from .selectors import CallSelectors, ConversationSelectors, MessageSelectors
from .serializers import (
    CallLogSerializer, ConversationSerializer, CreateDirectConversationSerializer,
    InitiateCallSerializer, MessageSerializer, SendMessageSerializer, TypingSerializer,
)
from .services import CallService, ConversationService, MessageService

logger = logging.getLogger('carebridge')


def _get_conversation_or_404(conversation_id):
    conv = ConversationRepository.get_by_id(conversation_id)
    if not conv:
        raise ConversationNotFoundException()
    return conv


def _get_message_or_404(message_id):
    msg = MessageRepository.get_by_id(message_id)
    if not msg:
        raise MessageNotFoundException()
    return msg


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

@extend_schema(tags=['Communication'])
class ConversationListView(APIView):
    """List all conversations for the authenticated user."""
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: ConversationSerializer(many=True)}, summary='List my conversations')
    def get(self, request):
        conversations = ConversationSelectors.get_user_conversations(request.user.id)
        return success_response(
            ConversationSerializer(conversations, many=True, context={'request': request}).data
        )


@extend_schema(tags=['Communication'])
class CreateDirectConversationView(APIView):
    """Create a direct conversation with another user."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CreateDirectConversationSerializer,
        responses={201: ConversationSerializer},
        summary='Start a direct conversation',
    )
    def post(self, request):
        serializer = CreateDirectConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            recipient = User.objects.get(id=serializer.validated_data['recipient_id'])
        except User.DoesNotExist:
            raise ResourceNotFoundException('Recipient user not found.')
        conversation = ConversationService.create_direct_conversation(request.user, recipient)
        return created_response(
            ConversationSerializer(conversation, context={'request': request}).data,
            message='Conversation created.',
        )


@extend_schema(tags=['Communication'])
class ConversationDetailView(APIView):
    """Retrieve or close a conversation."""
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    @extend_schema(responses={200: ConversationSerializer}, summary='Get conversation detail')
    def get(self, request, conversation_id):
        conv = _get_conversation_or_404(conversation_id)
        return success_response(ConversationSerializer(conv, context={'request': request}).data)

    @extend_schema(responses={200: ConversationSerializer}, summary='Close a conversation')
    def delete(self, request, conversation_id):
        conv = _get_conversation_or_404(conversation_id)
        conv = ConversationService.close_conversation(conv, request.user)
        return success_response(ConversationSerializer(conv, context={'request': request}).data, message='Conversation closed.')


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

@extend_schema(tags=['Communication'])
class MessageListView(APIView):
    """List messages in a conversation (cursor-paginated) or send a new message."""
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    @extend_schema(responses={200: MessageSerializer(many=True)}, summary='List messages')
    def get(self, request, conversation_id):
        _get_conversation_or_404(conversation_id)
        before_id = request.query_params.get('before')
        limit = min(int(request.query_params.get('limit', 50)), 100)
        messages = MessageSelectors.get_messages(conversation_id, before_id, limit)
        # Mark delivered for the requesting user
        MessageRepository.mark_delivered(conversation_id, exclude_sender_id=request.user.id)
        return success_response(MessageSerializer(messages, many=True).data)

    @extend_schema(request=SendMessageSerializer, responses={201: MessageSerializer}, summary='Send a message')
    def post(self, request, conversation_id):
        conv = _get_conversation_or_404(conversation_id)
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = MessageService.send_message(conv, request.user, serializer.validated_data)
        return created_response(MessageSerializer(message).data, message='Message sent.')


@extend_schema(tags=['Communication'])
class MessageDeleteView(APIView):
    """Soft-delete a message (sender only)."""
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    @extend_schema(responses={200: dict}, summary='Delete a message')
    def delete(self, request, conversation_id, message_id):
        _get_conversation_or_404(conversation_id)
        msg = _get_message_or_404(message_id)
        MessageService.delete_message(msg, request.user)
        return deleted_response('Message deleted.')


@extend_schema(tags=['Communication'])
class MarkReadView(APIView):
    """Mark all messages in a conversation as read."""
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    @extend_schema(responses={200: dict}, summary='Mark conversation as read')
    def post(self, request, conversation_id):
        conv = _get_conversation_or_404(conversation_id)
        MessageService.mark_conversation_read(conv, request.user)
        return success_response(message='Marked as read.')


@extend_schema(tags=['Communication'])
class TypingView(APIView):
    """Broadcast typing indicator to conversation participants."""
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    @extend_schema(request=TypingSerializer, responses={200: dict}, summary='Send typing indicator')
    def post(self, request, conversation_id):
        _get_conversation_or_404(conversation_id)
        serializer = TypingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        MessageService.broadcast_typing(
            conversation_id, request.user,
            serializer.validated_data['is_typing'],
        )
        return success_response(message='Typing status broadcast.')


# ---------------------------------------------------------------------------
# Calls
# ---------------------------------------------------------------------------

@extend_schema(tags=['Communication'])
class CallListView(APIView):
    """List call history for a conversation or initiate a new call."""
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    @extend_schema(responses={200: CallLogSerializer(many=True)}, summary='List call history')
    def get(self, request, conversation_id):
        _get_conversation_or_404(conversation_id)
        calls = CallSelectors.get_call_history(conversation_id)
        return success_response(CallLogSerializer(calls, many=True).data)

    @extend_schema(request=InitiateCallSerializer, responses={201: CallLogSerializer}, summary='Initiate a call')
    def post(self, request, conversation_id):
        conv = _get_conversation_or_404(conversation_id)
        serializer = InitiateCallSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            receiver = User.objects.get(id=serializer.validated_data['receiver_id'])
        except User.DoesNotExist:
            raise ResourceNotFoundException('Receiver user not found.')
        call = CallService.initiate_call(conv, request.user, receiver, serializer.validated_data['call_type'])
        return created_response(CallLogSerializer(call).data, message='Call initiated.')


@extend_schema(tags=['Communication'])
class CallAnswerView(APIView):
    """Answer an incoming call."""
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    @extend_schema(responses={200: CallLogSerializer}, summary='Answer a call')
    def post(self, request, conversation_id, call_id):
        call = CallLogRepository.get_by_id(call_id)
        if not call:
            raise CallNotFoundException()
        call = CallService.answer_call(call, request.user)
        return success_response(CallLogSerializer(call).data, message='Call answered.')


@extend_schema(tags=['Communication'])
class CallDeclineView(APIView):
    """Decline an incoming call."""
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    @extend_schema(responses={200: CallLogSerializer}, summary='Decline a call')
    def post(self, request, conversation_id, call_id):
        call = CallLogRepository.get_by_id(call_id)
        if not call:
            raise CallNotFoundException()
        call = CallService.decline_call(call, request.user)
        return success_response(CallLogSerializer(call).data, message='Call declined.')


@extend_schema(tags=['Communication'])
class CallEndView(APIView):
    """End an active call."""
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    @extend_schema(responses={200: CallLogSerializer}, summary='End a call')
    def post(self, request, conversation_id, call_id):
        call = CallLogRepository.get_by_id(call_id)
        if not call:
            raise CallNotFoundException()
        call = CallService.end_call(call, request.user)
        return success_response(CallLogSerializer(call).data, message='Call ended.')
