"""Notifications admin configuration."""
from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notification_type', 'channel', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'channel', 'priority', 'is_read']
    search_fields = ['user__email', 'title']
    readonly_fields = ['id', 'created_at', 'read_at']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'in_app_enabled', 'email_enabled', 'sms_enabled', 'push_enabled']
    search_fields = ['user__email']
