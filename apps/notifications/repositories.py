"""Notifications repositories — DB access layer."""
from django.utils import timezone
from .models import Notification, NotificationPreference


class NotificationRepository:

    @staticmethod
    def get_for_user(user_id, unread_only=False):
        qs = Notification.objects.filter(user_id=user_id)
        if unread_only:
            qs = qs.filter(is_read=False)
        return qs.order_by('-created_at')

    @staticmethod
    def get_by_id(notification_id):
        return Notification.objects.filter(id=notification_id).first()

    @staticmethod
    def create(user_id, notification_type, title, body, channel, priority, data=None, action_url=''):
        return Notification.objects.create(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            body=body,
            channel=channel,
            priority=priority,
            data=data or {},
            action_url=action_url,
        )

    @staticmethod
    def mark_read(notification_id, user_id):
        return Notification.objects.filter(
            id=notification_id, user_id=user_id, is_read=False,
        ).update(is_read=True, read_at=timezone.now())

    @staticmethod
    def mark_all_read(user_id):
        return Notification.objects.filter(
            user_id=user_id, is_read=False,
        ).update(is_read=True, read_at=timezone.now())

    @staticmethod
    def delete(notification_id, user_id):
        return Notification.objects.filter(id=notification_id, user_id=user_id).delete()

    @staticmethod
    def unread_count(user_id):
        return Notification.objects.filter(user_id=user_id, is_read=False).count()


class PreferenceRepository:

    @staticmethod
    def get_or_create(user_id):
        pref, _ = NotificationPreference.objects.get_or_create(user_id=user_id)
        return pref

    @staticmethod
    def update(user_id, **fields):
        NotificationPreference.objects.update_or_create(
            user_id=user_id, defaults=fields,
        )
        return PreferenceRepository.get_or_create(user_id)
