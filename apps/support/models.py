"""Support models — Ticket, TicketMessage, FAQ, ChatbotLog."""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from . import constants

User = get_user_model()


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets', db_index=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_tickets',
    )
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=15, choices=constants.TICKET_CATEGORY_CHOICES,
        default=constants.TICKET_CATEGORY_OTHER, db_index=True,
    )
    priority = models.CharField(
        max_length=10, choices=constants.TICKET_PRIORITY_CHOICES,
        default=constants.TICKET_PRIORITY_MEDIUM, db_index=True,
    )
    status = models.CharField(
        max_length=15, choices=constants.TICKET_STATUS_CHOICES,
        default=constants.TICKET_STATUS_OPEN, db_index=True,
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'priority']),
        ]

    def __str__(self):
        return f"Ticket {self.id} — {self.subject} [{self.status}]"


class TicketMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages', db_index=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_messages')
    body = models.TextField()
    is_staff_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"Message on Ticket {self.ticket_id} by {self.sender_id}"


class FAQ(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(
        max_length=15, choices=constants.FAQ_CATEGORY_CHOICES,
        default=constants.FAQ_CATEGORY_GENERAL, db_index=True,
    )
    question = models.CharField(max_length=500)
    answer = models.TextField()
    is_published = models.BooleanField(default=True, db_index=True)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'faqs'
        ordering = ['category', 'order']

    def __str__(self):
        return f"FAQ: {self.question[:60]}"


class ChatbotLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbot_logs', db_index=True)
    user_message = models.TextField()
    bot_response = models.TextField()
    intent = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chatbot_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"ChatbotLog {self.id} — {self.user_id}"
