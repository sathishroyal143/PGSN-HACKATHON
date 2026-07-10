"""Care Journey signals — auto-create journey when booking goes IN_PROGRESS."""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='bookings.BookingStatusLog')
def auto_start_journey(sender, instance, created, **kwargs):
    if not created:
        return
    from apps.bookings.constants import STATUS_IN_PROGRESS
    if instance.to_status != STATUS_IN_PROGRESS:
        return
    from .services import CareJourneyService
    from .repositories import CareJourneyRepository
    booking_id = instance.booking_id
    if not CareJourneyRepository.get_by_booking(booking_id):
        try:
            CareJourneyService.start_journey(booking_id, instance.changed_by)
        except Exception:
            pass
