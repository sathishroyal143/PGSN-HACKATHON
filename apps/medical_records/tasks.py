"""Celery tasks for Medical Records."""
import logging
from config.celery import app

logger = logging.getLogger('carebridge')


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_medical_summary_task(self, record_id):
    """Generate AI summary for a medical record asynchronously."""
    try:
        from apps.medical_records.models import MedicalRecord
        record = MedicalRecord.objects.get(id=record_id, is_deleted=False)

        text = f"Diagnosis: {record.diagnosis}\nTreatment: {record.treatment_notes}"
        if not text.strip():
            return

        # Attempt AI summary — gracefully skip if AI engine unavailable
        try:
            from apps.ai_engine.medical_summary import generate_summary
            summary = generate_summary(text)
        except Exception as ai_exc:
            logger.warning(f"AI summary skipped for record {record_id}: {ai_exc}")
            return

        record.ai_summary = summary
        record.save(update_fields=['ai_summary'])
        logger.info(f"AI summary generated for record {record_id}")

    except MedicalRecord.DoesNotExist:
        logger.warning(f"Record {record_id} not found for AI summary.")
    except Exception as exc:
        logger.error(f"AI summary task failed for {record_id}: {exc}")
        raise self.retry(exc=exc)
