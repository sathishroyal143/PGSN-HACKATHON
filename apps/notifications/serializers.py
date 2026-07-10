"""Notifications serializers."""
from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'channel', 'priority',
            'title', 'body', 'data', 'is_read', 'read_at',
            'action_url', 'created_at',
        ]
        read_only_fields = fields


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['in_app_enabled', 'email_enabled', 'sms_enabled', 'push_enabled', 'muted_types', 'updated_at']
        read_only_fields = ['updated_at']
