"""Notifications selectors — read-only queries."""
from .repositories import NotificationRepository, PreferenceRepository


class NotificationSelectors:

    @staticmethod
    def list_for_user(user_id, unread_only=False):
        return NotificationRepository.get_for_user(user_id, unread_only=unread_only)

    @staticmethod
    def unread_count(user_id):
        return NotificationRepository.unread_count(user_id)

    @staticmethod
    def get_preferences(user_id):
        return PreferenceRepository.get_or_create(user_id)
