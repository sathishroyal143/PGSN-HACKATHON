"""
URL configuration for CareBridge-AI project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def health_check(request):
    """Liveness + readiness probe — checks DB and Redis."""
    status = {'status': 'ok', 'db': 'ok', 'redis': 'ok'}
    http_status = 200

    # Database check
    try:
        from django.db import connection
        connection.ensure_connection()
    except Exception as exc:
        status['db'] = str(exc)
        status['status'] = 'degraded'
        http_status = 503

    # Redis check
    try:
        import redis as _redis
        from decouple import config as _cfg
        r = _redis.Redis(
            host=_cfg('REDIS_HOST', default='localhost'),
            port=_cfg('REDIS_PORT', default=6379, cast=int),
            socket_connect_timeout=1,
        )
        r.ping()
    except Exception:
        status['redis'] = 'unavailable'

    return JsonResponse(status, status=http_status)

urlpatterns = [
    path('health/', health_check, name='health'),
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 Endpoints
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/family/', include('apps.family.urls')),
    path('api/v1/patients/', include('apps.patients.urls')),
    path('api/v1/medical-records/', include('apps.medical_records.urls')),
    path('api/v1/companions/', include('apps.companions.urls')),
    path('api/v1/services/', include('apps.services.urls')),
    path('api/v1/bookings/', include('apps.bookings.urls')),
    path('api/v1/care-journey/', include('apps.care_journey.urls')),
    path('api/v1/tracking/', include('apps.live_tracking.urls')),
    path('api/v1/communication/', include('apps.communication.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/reviews/', include('apps.reviews.urls')),
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/support/', include('apps.support.urls')),
    path('api/v1/verification/', include('apps.document_verification.urls')),
    path('api/v1/ai/', include('apps.ai_engine.urls')),
    path('api/v1/gateway/', include('apps.api_gateway.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = 'CareBridge-AI Administration'
admin.site.site_title = 'CareBridge-AI Admin'
admin.site.index_title = 'Welcome to CareBridge-AI Administration'
