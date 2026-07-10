"""Communication admin configuration."""
from django.contrib import admin
from .models import CallLog, Conversation, ConversationParticipant, Message, MessageReadReceipt


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation_type', 'status', 'title', 'last_message_at', 'created_at']
    list_filter = ['conversation_type', 'status']
    search_fields = ['title', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ConversationParticipant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'user', 'unread_count', 'is_active', 'joined_at']
    list_filter = ['is_active']
    search_fields = ['user__email', 'conversation__id']
    readonly_fields = ['id', 'joined_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'message_type', 'status', 'is_deleted', 'created_at']
    list_filter = ['message_type', 'status', 'is_deleted']
    search_fields = ['sender__email', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(MessageReadReceipt)
class ReadReceiptAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'user', 'read_at']
    search_fields = ['user__email']
    readonly_fields = ['id', 'read_at']


@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'caller', 'receiver', 'call_type', 'status', 'duration_seconds', 'created_at']
    list_filter = ['call_type', 'status']
    search_fields = ['caller__email', 'receiver__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
