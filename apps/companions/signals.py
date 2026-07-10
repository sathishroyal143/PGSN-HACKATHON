"""Companions signals — auto-create profile when COMPANION user registers."""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.users.models import UserRole

logger = logging.getLogger('carebridge')
User = get_user_model()


@receiver(post_save, sender=User)
def create_companion_profile(sender, instance, created, **kwargs):
    if created and instance.role == UserRole.COMPANION:
        from .models import CompanionProfile
        CompanionProfile.objects.get_or_create(user=instance)
        logger.info(f"CompanionProfile auto-created for user {instance.id}")
