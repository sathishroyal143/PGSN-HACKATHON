"""
Signals for Medical Records.
Triggers AI summary generation asynchronously after a record is saved.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MedicalRecord

logger = logging.getLogger('carebridge')


@receiver(post_save, sender=MedicalRecord)
def trigger_ai_summary(sender, instance, created, **kwargs):
    """
    After a MedicalRecord is created or updated, queue an AI summary task.
    Only triggers when diagnosis or treatment_notes are present.
    """
    if not (instance.diagnosis or instance.treatment_notes):
        return
    try:
        from apps.medical_records.tasks import generate_medical_summary_task
        generate_medical_summary_task.delay(str(instance.id))
    except Exception as exc:
        logger.warning(f"Could not queue AI summary for record {instance.id}: {exc}")
