"""
Care Services signals.
Post-save hooks for audit logging.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ServicePackage, CareService

logger = logging.getLogger('carebridge')


@receiver(post_save, sender=ServicePackage)
def log_package_created(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New ServicePackage created: {instance.id} — {instance.name}")


@receiver(post_save, sender=CareService)
def log_care_service_saved(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"CareService created: {instance.id} — {instance.service_code} "
            f"[{instance.service_category.code}]"
        )
    else:
        logger.debug(
            f"CareService updated: {instance.id} — status={instance.status} "
            f"deleted={instance.is_deleted}"
        )
