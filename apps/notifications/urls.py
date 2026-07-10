"""Notifications URL configuration."""
from django.urls import path
from .views import (
    NotificationListView, MarkReadView, MarkAllReadView,
    NotificationDeleteView, NotificationPreferenceView,
)

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='list'),
    path('read-all/', MarkAllReadView.as_view(), name='read-all'),
    path('preferences/', NotificationPreferenceView.as_view(), name='preferences'),
    path('<uuid:notification_id>/read/', MarkReadView.as_view(), name='read'),
    path('<uuid:notification_id>/', NotificationDeleteView.as_view(), name='delete'),
]
