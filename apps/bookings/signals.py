"""Bookings signals."""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from . import constants

logger = logging.getLogger('carebridge')


@receiver(post_save, sender=Booking)
def booking_status_changed(sender, instance, created, **kwargs):
    if not created and instance.status == constants.STATUS_COMPLETED:
        logger.info(f"Booking {instance.id} completed. Final price: {instance.final_price}")
        if instance.companion and hasattr(instance.companion, 'companion_profile'):
            profile = instance.companion.companion_profile
            count = Booking.objects.filter(companion=instance.companion, status=constants.STATUS_COMPLETED).count()
            profile.total_bookings_completed = count
            profile.save(update_fields=['total_bookings_completed'])
