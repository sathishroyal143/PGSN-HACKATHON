"""URL configuration for API Gateway administration."""
from django.urls import path

from .views import (
    APIKeyListView,
    AuditLogListView,
    GatewayStatisticsView,
    RateLimitDetailView,
    RateLimitListView,
    RevokeAPIKeyView,
)

app_name = 'api_gateway'

urlpatterns = [
    path('keys/', APIKeyListView.as_view(), name='keys'),
    path('keys/<uuid:pk>/revoke/', RevokeAPIKeyView.as_view(), name='revoke-key'),
    path('rate-limits/', RateLimitListView.as_view(), name='rate-limits'),
    path('rate-limits/<uuid:pk>/', RateLimitDetailView.as_view(), name='rate-limit-detail'),
    path('audit-logs/', AuditLogListView.as_view(), name='audit-logs'),
    path('statistics/', GatewayStatisticsView.as_view(), name='statistics'),
]
