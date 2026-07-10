"""Live Tracking Celery tasks."""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('carebridge')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_stale_location_updates(self, days: int = 30):
    """
    Delete location updates older than `days` days to keep the table lean.
    Runs nightly via Celery Beat.
    """
    from apps.live_tracking.models import LocationUpdate
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = LocationUpdate.objects.filter(recorded_at__lt=cutoff).delete()
    logger.info("Cleaned up %d stale location updates older than %d days.", deleted, days)
    return deleted


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def broadcast_eta_update(self, booking_id: str, route_id: str):
    """
    Recalculate and broadcast ETA for an active route.
    Called periodically while a booking is in_progress.
    """
    from apps.live_tracking.models import Route
    from apps.live_tracking.repositories import LocationUpdateRepository, RouteRepository
    from apps.live_tracking.services import _broadcast
    from apps.live_tracking import constants

    route = RouteRepository.get_by_id(route_id)
    if not route or route.status != constants.ROUTE_STATUS_ACTIVE:
        return

    latest = LocationUpdateRepository.get_latest_for_booking(booking_id)
    if not latest or not route.duration_seconds:
        return

    # Simple ETA: current time + remaining duration (no external API call)
    new_eta = timezone.now() + timedelta(seconds=route.duration_seconds)
    RouteRepository.update_eta(route, new_eta)

    _broadcast(booking_id, constants.WS_TYPE_ETA_UPDATE, {
        'booking_id': booking_id,
        'route_id': route_id,
        'estimated_arrival': new_eta.isoformat(),
    })
    logger.info("ETA updated for booking %s route %s → %s", booking_id, route_id, new_eta)
