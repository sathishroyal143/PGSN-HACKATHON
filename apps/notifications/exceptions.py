"""Notifications exceptions."""
from rest_framework.exceptions import APIException, NotFound
from rest_framework import status


class NotificationNotFoundException(NotFound):
    default_detail = 'Notification not found.'


class NotificationAccessDeniedException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have access to this notification.'
