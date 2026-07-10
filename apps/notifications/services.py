"""Notifications services — business logic."""
import logging
from . import constants
from .repositories import NotificationRepository, PreferenceRepository
from .exceptions import NotificationNotFoundException, NotificationAccessDeniedException

logger = logging.getLogger('carebridge')


class NotificationService:

    @staticmethod
    def send(user_id, notification_type, title, body,
             channel=constants.CHANNEL_IN_APP,
             priority=constants.PRIORITY_NORMAL,
             data=None, action_url=''):
        """Create an in-app notification record. Extend here for push/email/SMS."""
        notif = NotificationRepository.create(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            body=body,
            channel=channel,
            priority=priority,
            data=data or {},
            action_url=action_url,
        )
        logger.info("Notification sent user=%s type=%s", user_id, notification_type)
        return notif

    @staticmethod
    def mark_read(notification_id, user_id):
        notif = NotificationRepository.get_by_id(notification_id)
        if not notif:
            raise NotificationNotFoundException()
        if str(notif.user_id) != str(user_id):
            raise NotificationAccessDeniedException()
        NotificationRepository.mark_read(notification_id, user_id)

    @staticmethod
    def mark_all_read(user_id):
        return NotificationRepository.mark_all_read(user_id)

    @staticmethod
    def delete(notification_id, user_id):
        notif = NotificationRepository.get_by_id(notification_id)
        if not notif:
            raise NotificationNotFoundException()
        if str(notif.user_id) != str(user_id):
            raise NotificationAccessDeniedException()
        NotificationRepository.delete(notification_id, user_id)

    @staticmethod
    def update_preferences(user_id, **fields):
        return PreferenceRepository.update(user_id, **fields)
