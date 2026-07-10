"""Notifications models — Notification, NotificationPreference."""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from . import constants

User = get_user_model()


class Notification(models.Model):
    """In-app notification record for a user."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='notifications', db_index=True,
    )
    notification_type = models.CharField(
        max_length=40, choices=constants.NOTIF_TYPE_CHOICES, db_index=True,
    )
    channel = models.CharField(
        max_length=10, choices=constants.CHANNEL_CHOICES,
        default=constants.CHANNEL_IN_APP,
    )
    priority = models.CharField(
        max_length=10, choices=constants.PRIORITY_CHOICES,
        default=constants.PRIORITY_NORMAL,
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)

    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # Optional deep-link reference
    action_url = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['user', 'notification_type']),
        ]

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → {self.user_id}"


class NotificationPreference(models.Model):
    """Per-user, per-type channel preferences."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='notification_preference',
    )
    # Global toggles (mirrors User model flags but owned here)
    in_app_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)

    # Fine-grained per-type mutes stored as JSON list of muted types
    muted_types = models.JSONField(default=list, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'

    def __str__(self):
        return f"NotifPrefs — {self.user_id}"
