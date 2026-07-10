from django.apps import AppConfig


class CareJourneyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.care_journey'
    verbose_name = 'Care Journey'

    def ready(self):
        import apps.care_journey.signals  # noqa
