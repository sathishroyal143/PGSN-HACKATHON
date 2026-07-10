"""Live Tracking signals — auto-create geofences on booking confirmation."""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.bookings.models import Booking

logger = logging.getLogger('carebridge')


@receiver(post_save, sender=Booking)
def create_geofences_on_booking_confirm(sender, instance: Booking, created: bool, **kwargs):
    """
    When a booking moves to 'confirmed' or 'in_progress' for the first time,
    auto-create pickup and hospital geofences so the tracking system is ready.
    """
    if instance.status not in ('confirmed', 'in_progress'):
        return

    # Only create if no geofences exist yet for this booking
    from apps.live_tracking.models import Geofence
    if Geofence.objects.filter(booking=instance).exists():
        return

    try:
        from apps.live_tracking.services import GeofenceService
        GeofenceService.create_geofences_for_booking(instance)
    except Exception as exc:
        logger.error("Failed to auto-create geofences for booking %s: %s", instance.id, exc)
