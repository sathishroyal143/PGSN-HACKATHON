"""Notifications signals — fire notifications on key domain events."""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger('carebridge')


@receiver(post_save, sender='bookings.Booking')
def notify_booking_status_change(sender, instance, created, **kwargs):
    from apps.notifications.services import NotificationService
    from apps.notifications import constants

    if created:
        NotificationService.send(
            user_id=instance.family_user_id,
            notification_type=constants.NOTIF_TYPE_BOOKING_CONFIRMED,
            title='Booking Created',
            body=f'Your booking #{str(instance.id)[:8]} has been created.',
            data={'booking_id': str(instance.id)},
            action_url=f'/family/bookings/{instance.id}',
        )
        # Notify companions of the new request
        from django.contrib.auth import get_user_model
        User = get_user_model()
        companions = User.objects.filter(role='COMPANION')
        for companion in companions:
            try:
                NotificationService.send(
                    user_id=companion.id,
                    notification_type=constants.NOTIF_TYPE_SYSTEM,
                    title='New Care Request',
                    body=f'A new care request for {instance.patient.first_name} is available.',
                    data={'booking_id': str(instance.id)},
                    action_url=f'/companion/bookings/{instance.id}',
                )
            except Exception as exc:
                logger.error("Failed to send companion new booking notification: %s", exc)
        return

    status_map = {
        'CONFIRMED': (constants.NOTIF_TYPE_BOOKING_CONFIRMED, 'Booking Confirmed',
                      f'Your booking #{str(instance.id)[:8]} is confirmed.'),
        'CANCELLED': (constants.NOTIF_TYPE_BOOKING_CANCELLED, 'Booking Cancelled',
                      f'Your booking #{str(instance.id)[:8]} has been cancelled.'),
        'COMPLETED': (constants.NOTIF_TYPE_BOOKING_COMPLETED, 'Booking Completed',
                      f'Your booking #{str(instance.id)[:8]} is complete.'),
    }

    entry = status_map.get(instance.status)
    if not entry:
        return

    notif_type, title, body = entry
    try:
        NotificationService.send(
            user_id=instance.family_user_id,
            notification_type=notif_type,
            title=title,
            body=body,
            data={'booking_id': str(instance.id)},
            action_url=f'/family/bookings/{instance.id}',
        )
    except Exception as exc:
        logger.error("Failed to send booking notification: %s", exc)

    # Notify companion if the booking is cancelled
    if instance.status == 'CANCELLED' and instance.companion_id:
        try:
            NotificationService.send(
                user_id=instance.companion_id,
                notification_type=constants.NOTIF_TYPE_BOOKING_CANCELLED,
                title='Booking Cancelled',
                body=f'The booking #{str(instance.id)[:8]} has been cancelled by the family.',
                data={'booking_id': str(instance.id)},
                action_url=f'/companion/bookings/{instance.id}',
            )
        except Exception as exc:
            logger.error("Failed to send companion cancellation notification: %s", exc)
