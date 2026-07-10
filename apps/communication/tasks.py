"""Communication Celery tasks."""
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('carebridge')


@shared_task(bind=True, max_retries=2)
def mark_missed_calls(self):
    """
    Mark calls that have been ringing for more than 60 seconds as missed.
    Runs every minute via Celery Beat.
    """
    from apps.communication.models import CallLog
    from apps.communication import constants

    cutoff = timezone.now() - timedelta(seconds=60)
    missed = CallLog.objects.filter(
        status=constants.CALL_STATUS_RINGING,
        started_at__lt=cutoff,
    )
    count = missed.update(
        status=constants.CALL_STATUS_MISSED,
        ended_at=timezone.now(),
    )
    if count:
        logger.info("Marked %d calls as missed.", count)
    return count
