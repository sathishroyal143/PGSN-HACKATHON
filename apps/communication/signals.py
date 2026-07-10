"""Communication signals — auto-create conversation on booking confirmation."""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.bookings.models import Booking

logger = logging.getLogger('carebridge')


@receiver(post_save, sender=Booking)
def create_conversation_on_booking_confirm(sender, instance: Booking, created: bool, **kwargs):
    """
    When a booking is confirmed and a companion is assigned,
    auto-create the booking conversation so both parties can chat immediately.
    """
    if instance.status.upper() not in ['CONFIRMED', 'COMPANION_ASSIGNED', 'IN_PROGRESS'] or not instance.companion_id:
        return

    from apps.communication.models import Conversation
    if Conversation.objects.filter(booking=instance).exists():
        return

    try:
        from apps.communication.services import ConversationService
        ConversationService.get_or_create_booking_conversation(instance)
    except Exception as exc:
        logger.error("Failed to auto-create conversation for booking %s: %s", instance.id, exc)
