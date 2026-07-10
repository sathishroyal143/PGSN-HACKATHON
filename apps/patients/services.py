"""Service layer for the Patients module."""
import logging
from django.db import transaction
from .repositories import PatientRepository, PatientVitalRepository, PatientInsuranceRepository
from .exceptions import (
    PatientNotFoundException,
    PatientLimitExceededException,
    VitalNotFoundException,
    InsuranceNotFoundException,
    InsuranceAlreadyExistsException,
    PatientAccessDeniedException,
    NoFamilyProfileException,
)
from . import constants

logger = logging.getLogger('carebridge')


class PatientService:

    @staticmethod
    @transaction.atomic
    def create_patient(family_profile, patient_data):
        count = PatientRepository.count_by_family_profile(family_profile)
        if count >= constants.MAX_PATIENTS_PER_FAMILY:
            raise PatientLimitExceededException(constants.ERR_PATIENT_LIMIT)

        # First patient is automatically primary
        if count == 0:
            patient_data['is_primary'] = True

        patient_data['family_profile'] = family_profile
        patient = PatientRepository.create(patient_data)
        logger.info(f"Patient created: {patient.id} for family {family_profile.id}")
        return patient

    @staticmethod
    @transaction.atomic
    def update_patient(patient, patient_data):
        patient = PatientRepository.update(patient, patient_data)
        logger.info(f"Patient updated: {patient.id}")
        return patient

    @staticmethod
    @transaction.atomic
    def delete_patient(patient):
        PatientRepository.soft_delete(patient)
        logger.info(f"Patient soft-deleted: {patient.id}")
        return True

    @staticmethod
    @transaction.atomic
    def set_primary_patient(patient):
        PatientRepository.set_primary(patient)
        logger.info(f"Patient set as primary: {patient.id}")
        return patient

    @staticmethod
    def get_patient_or_raise(patient_id):
        patient = PatientRepository.get_by_id(patient_id)
        if not patient:
            raise PatientNotFoundException()
        return patient

    @staticmethod
    def assert_family_owns_patient(family_profile, patient):
        if patient.family_profile_id != family_profile.id:
            raise PatientAccessDeniedException()


class PatientVitalService:

    @staticmethod
    @transaction.atomic
    def record_vital(patient, vital_data, recorded_by=''):
        vital_data['patient'] = patient
        vital_data['recorded_by'] = recorded_by
        vital = PatientVitalRepository.create(vital_data)
        logger.info(f"Vital recorded for patient: {patient.id}")
        return vital

    @staticmethod
    @transaction.atomic
    def delete_vital(vital_id, patient):
        vital = PatientVitalRepository.get_by_id(vital_id)
        if not vital or vital.patient_id != patient.id:
            raise VitalNotFoundException()
        PatientVitalRepository.delete(vital)
        logger.info(f"Vital deleted: {vital_id}")
        return True


class PatientInsuranceService:

    @staticmethod
    @transaction.atomic
    def add_insurance(patient, insurance_data):
        if PatientInsuranceRepository.has_active(patient):
            raise InsuranceAlreadyExistsException()
        insurance_data['patient'] = patient
        insurance = PatientInsuranceRepository.create(insurance_data)
        logger.info(f"Insurance added for patient: {patient.id}")
        return insurance

    @staticmethod
    @transaction.atomic
    def update_insurance(insurance, insurance_data):
        insurance = PatientInsuranceRepository.update(insurance, insurance_data)
        logger.info(f"Insurance updated: {insurance.id}")
        return insurance

    @staticmethod
    @transaction.atomic
    def deactivate_insurance(insurance_id, patient):
        insurance = PatientInsuranceRepository.get_by_id(insurance_id)
        if not insurance or insurance.patient_id != patient.id:
            raise InsuranceNotFoundException()
        PatientInsuranceRepository.deactivate(insurance)
        logger.info(f"Insurance deactivated: {insurance_id}")
        return True
