"""
Signals for Family module.
Auto-creates FamilyProfile when a User with role=FAMILY is created or updated to FAMILY.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def create_family_profile(sender, instance, created, **kwargs):
    """Auto-create FamilyProfile for FAMILY role users."""
    from apps.users.models import UserRole
    from apps.family.models import FamilyProfile

    if instance.role != UserRole.FAMILY:
        return

    if not FamilyProfile.objects.filter(user=instance, is_deleted=False).exists():
        FamilyProfile.objects.create(user=instance)
        logger.info(f'FamilyProfile auto-created for user {instance.email}')
