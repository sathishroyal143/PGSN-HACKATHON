"""
Django app configuration for Family module.
"""
from django.apps import AppConfig


class FamilyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.family'
    verbose_name = 'Family'

    def ready(self):
        import apps.family.signals
