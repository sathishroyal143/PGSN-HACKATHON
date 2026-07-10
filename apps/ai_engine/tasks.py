"""AI Engine Celery tasks — async execution for heavy AI operations."""
import logging
from config.celery import app

logger = logging.getLogger('carebridge')


@app.task(bind=True, max_retries=3, default_retry_delay=30)
def refresh_trust_score_task(self, companion_id, user_id):
    """Async trust score refresh — triggered on booking completion."""
    try:
        from apps.ai_engine.services import TrustScoreService
        _, output = TrustScoreService.run(user_id=user_id, companion_id=companion_id)
        logger.info('Trust score refreshed async companion=%s score=%s', companion_id, output.get('trust_score'))
    except Exception as exc:
        logger.error('refresh_trust_score_task failed companion=%s error=%s', companion_id, exc)
        raise self.retry(exc=exc)


@app.task(bind=True, max_retries=2, default_retry_delay=60)
def run_companion_match_task(self, user_id, patient_id, required_skills=None, top_n=10):
    """Async companion matching — for background pre-computation."""
    try:
        from apps.ai_engine.services import CompanionMatchService
        CompanionMatchService.run(
            user_id=user_id,
            patient_id=patient_id,
            required_skills=required_skills,
            top_n=top_n,
        )
        logger.info('Async companion match completed patient=%s', patient_id)
    except Exception as exc:
        logger.error('run_companion_match_task failed patient=%s error=%s', patient_id, exc)
        raise self.retry(exc=exc)
