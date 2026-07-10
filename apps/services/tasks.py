"""
Care Services Celery tasks.
Async operations dispatched via common.tasks.dispatch().
"""

import logging
from common.tasks import dispatch

logger = logging.getLogger('carebridge')


def notify_service_status_change(service_id: str, new_status: str) -> None:
    """
    Dispatch an async task to notify relevant parties when a CareService
    status changes (activated / deactivated / deleted).
    """
    dispatch(_log_service_status_change, service_id, new_status)


def _log_service_status_change(service_id: str, new_status: str) -> None:
    """
    Log a service status change event.
    Extend this to push notifications or audit events as needed.
    """
    logger.info(f"CareService {service_id} status changed to {new_status}")
