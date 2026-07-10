"""Communication models — Conversation, Message, CallLog."""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.bookings.models import Booking
from . import constants

User = get_user_model()


class Conversation(models.Model):
    """
    A thread between two or more participants.
    Booking conversations are auto-created when a booking is confirmed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation_type = models.CharField(
        max_length=10,
        choices=constants.CONV_TYPE_CHOICES,
        default=constants.CONV_TYPE_DIRECT,
        db_index=True,
    )
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='conversation',
    )
    status = models.CharField(
        max_length=10,
        choices=constants.CONV_STATUS_CHOICES,
        default=constants.CONV_STATUS_ACTIVE,
        db_index=True,
    )
    title = models.CharField(max_length=255, blank=True)
    last_message_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['conversation_type', 'status']),
        ]

    def __str__(self):
        return f"Conversation {self.id} [{self.conversation_type}]"


class ConversationParticipant(models.Model):
    """
    Junction table — which users belong to a conversation.
    Tracks per-participant unread count and last-read message.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE,
        related_name='participants', db_index=True,
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='conversation_participants', db_index=True,
    )
    unread_count = models.PositiveIntegerField(default=0)
    last_read_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversation_participants'
        verbose_name = 'Conversation Participant'
        unique_together = [('conversation', 'user')]
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} in {self.conversation_id}"


class Message(models.Model):
    """
    A single message within a conversation.
    Supports text, image, file, location, and system messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE,
        related_name='messages', db_index=True,
    )
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sent_messages',
    )
    message_type = models.CharField(
        max_length=10,
        choices=constants.MSG_TYPE_CHOICES,
        default=constants.MSG_TYPE_TEXT,
        db_index=True,
    )
    content = models.TextField(blank=True, max_length=constants.MAX_MESSAGE_LENGTH)
    file_url = models.URLField(blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)

    # For location messages
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Reply threading
    reply_to = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='replies',
    )

    status = models.CharField(
        max_length=10,
        choices=constants.MSG_STATUS_CHOICES,
        default=constants.MSG_STATUS_SENT,
        db_index=True,
    )

    # Soft delete (message retraction)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]

    def __str__(self):
        return f"Message {self.id} [{self.message_type}] in {self.conversation_id}"


class MessageReadReceipt(models.Model):
    """
    Tracks which users have read which messages.
    Normalized — one row per (message, user) pair.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE,
        related_name='read_receipts', db_index=True,
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='read_receipts',
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message_read_receipts'
        verbose_name = 'Message Read Receipt'
        unique_together = [('message', 'user')]
        indexes = [
            models.Index(fields=['message', 'user']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} read {self.message_id}"


class CallLog(models.Model):
    """
    Records every audio/video call attempt between participants.
    Duration is stored in seconds.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE,
        related_name='call_logs', db_index=True,
    )
    caller = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, related_name='outgoing_calls',
    )
    receiver = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, related_name='incoming_calls',
    )
    call_type = models.CharField(
        max_length=5,
        choices=constants.CALL_TYPE_CHOICES,
        default=constants.CALL_TYPE_AUDIO,
    )
    status = models.CharField(
        max_length=10,
        choices=constants.CALL_STATUS_CHOICES,
        default=constants.CALL_STATUS_INITIATED,
        db_index=True,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'call_logs'
        verbose_name = 'Call Log'
        verbose_name_plural = 'Call Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['caller', 'status']),
            models.Index(fields=['receiver', 'status']),
        ]

    def __str__(self):
        return f"Call {self.id} [{self.call_type}] [{self.status}]"
