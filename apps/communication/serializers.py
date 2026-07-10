"""Communication serializers."""
from rest_framework import serializers
from .models import CallLog, Conversation, ConversationParticipant, Message
from . import constants


class ParticipantSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ConversationParticipant
        fields = ['id', 'user', 'user_name', 'user_email', 'unread_count', 'last_read_at', 'joined_at']
        read_only_fields = fields


class ConversationSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'conversation_type', 'booking', 'status', 'title',
            'last_message_at', 'participants', 'unread_count', 'created_at',
        ]
        read_only_fields = fields

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
        participant = obj.participants.filter(user=request.user).first()
        return participant.unread_count if participant else 0


class CreateDirectConversationSerializer(serializers.Serializer):
    recipient_id = serializers.IntegerField()

    def validate_recipient_id(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError('Recipient user not found.')
        return value


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    reply_to_content = serializers.CharField(source='reply_to.content', read_only=True, default=None)

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_name',
            'message_type', 'content', 'file_url', 'file_name', 'file_size',
            'latitude', 'longitude', 'reply_to', 'reply_to_content',
            'status', 'is_deleted', 'created_at',
        ]
        read_only_fields = fields


class SendMessageSerializer(serializers.Serializer):
    message_type = serializers.ChoiceField(choices=constants.MSG_TYPE_CHOICES, default=constants.MSG_TYPE_TEXT)
    content = serializers.CharField(
        max_length=constants.MAX_MESSAGE_LENGTH,
        required=False, allow_blank=True, default='',
    )
    file_url = serializers.URLField(required=False, allow_blank=True, default='')
    file_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    file_size = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    reply_to = serializers.UUIDField(required=False, allow_null=True)

    def validate(self, attrs):
        msg_type = attrs.get('message_type', constants.MSG_TYPE_TEXT)
        if msg_type == constants.MSG_TYPE_TEXT and not attrs.get('content', '').strip():
            raise serializers.ValidationError({'content': 'Text messages require content.'})
        if msg_type in (constants.MSG_TYPE_IMAGE, constants.MSG_TYPE_FILE) and not attrs.get('file_url'):
            raise serializers.ValidationError({'file_url': 'File messages require a file_url.'})
        if msg_type == constants.MSG_TYPE_LOCATION:
            if attrs.get('latitude') is None or attrs.get('longitude') is None:
                raise serializers.ValidationError('Location messages require latitude and longitude.')
        if attrs.get('file_size') and attrs['file_size'] > constants.MAX_FILE_SIZE_BYTES:
            raise serializers.ValidationError({'file_size': 'File exceeds 10 MB limit.'})
        return attrs

    def validate_reply_to(self, value):
        if value:
            from .models import Message
            if not Message.objects.filter(id=value, is_deleted=False).exists():
                raise serializers.ValidationError('Reply-to message not found.')
        return value


class TypingSerializer(serializers.Serializer):
    is_typing = serializers.BooleanField()


class CallLogSerializer(serializers.ModelSerializer):
    caller_name = serializers.CharField(source='caller.get_full_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.get_full_name', read_only=True)

    class Meta:
        model = CallLog
        fields = [
            'id', 'conversation', 'caller', 'caller_name',
            'receiver', 'receiver_name', 'call_type', 'status',
            'started_at', 'answered_at', 'ended_at', 'duration_seconds', 'created_at',
        ]
        read_only_fields = fields


class InitiateCallSerializer(serializers.Serializer):
    receiver_id = serializers.IntegerField()
    call_type = serializers.ChoiceField(choices=constants.CALL_TYPE_CHOICES, default=constants.CALL_TYPE_AUDIO)

    def validate_receiver_id(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError('Receiver not found.')
        return value
