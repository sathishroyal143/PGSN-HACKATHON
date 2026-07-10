"""
Task dispatch helper — runs Celery tasks async if broker is available,
falls back to synchronous execution otherwise.
"""
import logging

logger = logging.getLogger('carebridge')


def _broker_available():
    try:
        from django.conf import settings
        import redis
        url = getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0')
        r = redis.Redis.from_url(url, socket_connect_timeout=1)
        r.ping()
        return True
    except Exception:
        return False


def dispatch(task_func, *args, **kwargs):
    """
    Dispatch a Celery task.
    - If broker is reachable: task_func.delay(*args, **kwargs)
    - Otherwise: call task_func directly (synchronous fallback)
    """
    if _broker_available():
        try:
            task_func.delay(*args, **kwargs)
            return
        except Exception as exc:
            logger.warning('Celery dispatch failed, running sync: %s', exc)
    # Synchronous fallback
    try:
        task_func(*args, **kwargs)
    except Exception as exc:
        logger.warning('Sync task fallback failed: %s', exc)
