"""
Signals for the Patients module.

Auto-creates a Patient record when a FamilyMember is created,
keeping the two models in sync without requiring manual API calls.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.family.models import FamilyMember

logger = logging.getLogger('carebridge')


@receiver(post_save, sender=FamilyMember)
def create_patient_for_family_member(sender, instance, created, **kwargs):
    """
    When a new FamilyMember is created, automatically create a linked Patient.
    Skips if a Patient already exists for this member.
    """
    if not created:
        return

    # Import here to avoid circular imports at module load time
    from apps.patients.models import Patient
    from apps.patients.repositories import PatientRepository

    if PatientRepository.get_by_family_member(instance):
        return

    count = PatientRepository.count_by_family_profile(instance.family_profile)
    from apps.patients import constants
    if count >= constants.MAX_PATIENTS_PER_FAMILY:
        logger.warning(
            f"Patient limit reached for family {instance.family_profile.id}; "
            f"skipping auto-create for FamilyMember {instance.id}"
        )
        return

    Patient.objects.create(
        family_profile=instance.family_profile,
        family_member=instance,
        first_name=instance.first_name,
        last_name=instance.last_name,
        date_of_birth=instance.date_of_birth,
        gender=instance.gender or '',
        blood_group=instance.blood_group or constants.BLOOD_GROUP_UNKNOWN,
        known_allergies=instance.known_allergies,
        chronic_conditions=instance.chronic_conditions,
        is_primary=instance.is_primary_patient,
        status=constants.STATUS_ACTIVE,
    )
    logger.info(
        f"Auto-created Patient for FamilyMember {instance.id} "
        f"in family {instance.family_profile.id}"
    )
