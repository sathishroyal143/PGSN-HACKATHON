from django.apps import AppConfig


class CompanionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.companions'
    verbose_name = 'Care Companions'

    def ready(self):
        import apps.companions.signals  # noqa
