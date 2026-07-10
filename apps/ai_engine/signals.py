"""AI Engine signals — auto-refresh trust score when companion completes a booking."""
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger('carebridge')


@receiver(post_save, sender='bookings.Booking')
def on_booking_completed(sender, instance, **kwargs):
    if instance.status == 'COMPLETED' and instance.companion_id:
        try:
            companion = instance.companion
            from apps.ai_engine.tasks import refresh_trust_score_task
            from common.tasks import dispatch
            dispatch(
                refresh_trust_score_task,
                companion_id=str(companion.id),
                user_id=instance.family_user_id,
            )
        except Exception as exc:
            logger.warning('on_booking_completed signal error: %s', exc)
