"""Live Tracking app configuration."""
from django.apps import AppConfig


class LiveTrackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.live_tracking'
    verbose_name = 'Live Tracking'

    def ready(self):
        import apps.live_tracking.signals  # noqa: F401
