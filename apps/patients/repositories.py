"""Repository layer for the Patients module."""
from django.db import transaction
from django.utils import timezone
from .models import Patient, PatientVital, PatientInsurance


class PatientRepository:

    @staticmethod
    def get_by_id(patient_id):
        try:
            return Patient.objects.select_related('family_profile', 'family_member').get(
                id=patient_id, is_deleted=False
            )
        except Patient.DoesNotExist:
            return None

    @staticmethod
    def get_by_family_profile(family_profile):
        return Patient.objects.filter(
            family_profile=family_profile, is_deleted=False
        ).order_by('-is_primary', 'first_name')

    @staticmethod
    def get_by_family_member(family_member):
        try:
            return Patient.objects.get(family_member=family_member, is_deleted=False)
        except Patient.DoesNotExist:
            return None

    @staticmethod
    def count_by_family_profile(family_profile):
        return Patient.objects.filter(
            family_profile=family_profile, is_deleted=False
        ).count()

    @staticmethod
    @transaction.atomic
    def create(patient_data):
        return Patient.objects.create(**patient_data)

    @staticmethod
    @transaction.atomic
    def update(patient, patient_data):
        for field, value in patient_data.items():
            setattr(patient, field, value)
        patient.save()
        return patient

    @staticmethod
    @transaction.atomic
    def soft_delete(patient):
        patient.is_deleted = True
        patient.deleted_at = timezone.now()
        patient.status = 'INACTIVE'
        patient.save(update_fields=['is_deleted', 'deleted_at', 'status'])
        return True

    @staticmethod
    def get_primary(family_profile):
        return Patient.objects.filter(
            family_profile=family_profile, is_primary=True, is_deleted=False
        ).first()

    @staticmethod
    @transaction.atomic
    def set_primary(patient):
        Patient.objects.filter(
            family_profile=patient.family_profile, is_primary=True
        ).update(is_primary=False)
        patient.is_primary = True
        patient.save(update_fields=['is_primary'])
        return patient


class PatientVitalRepository:

    @staticmethod
    def get_by_id(vital_id):
        try:
            return PatientVital.objects.select_related('patient').get(id=vital_id)
        except PatientVital.DoesNotExist:
            return None

    @staticmethod
    def get_by_patient(patient, limit=20):
        return PatientVital.objects.filter(patient=patient).order_by('-recorded_at')[:limit]

    @staticmethod
    def get_latest(patient):
        return PatientVital.objects.filter(patient=patient).order_by('-recorded_at').first()

    @staticmethod
    @transaction.atomic
    def create(vital_data):
        return PatientVital.objects.create(**vital_data)

    @staticmethod
    @transaction.atomic
    def delete(vital):
        vital.delete()
        return True


class PatientInsuranceRepository:

    @staticmethod
    def get_by_id(insurance_id):
        try:
            return PatientInsurance.objects.select_related('patient').get(id=insurance_id)
        except PatientInsurance.DoesNotExist:
            return None

    @staticmethod
    def get_active(patient):
        return PatientInsurance.objects.filter(patient=patient, is_active=True).first()

    @staticmethod
    def get_all_by_patient(patient):
        return PatientInsurance.objects.filter(patient=patient).order_by('-is_active', '-created_at')

    @staticmethod
    def has_active(patient):
        return PatientInsurance.objects.filter(patient=patient, is_active=True).exists()

    @staticmethod
    @transaction.atomic
    def create(insurance_data):
        return PatientInsurance.objects.create(**insurance_data)

    @staticmethod
    @transaction.atomic
    def update(insurance, insurance_data):
        for field, value in insurance_data.items():
            setattr(insurance, field, value)
        insurance.save()
        return insurance

    @staticmethod
    @transaction.atomic
    def deactivate(insurance):
        insurance.is_active = False
        insurance.save(update_fields=['is_active'])
        return True

    @staticmethod
    @transaction.atomic
    def delete(insurance):
        insurance.delete()
        return True
