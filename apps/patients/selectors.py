"""Selectors (read-only queries) for the Patients module."""
from .repositories import PatientRepository, PatientVitalRepository, PatientInsuranceRepository


class PatientSelector:

    @staticmethod
    def get_patient_summary(patient):
        latest_vital = PatientVitalRepository.get_latest(patient)
        active_insurance = PatientInsuranceRepository.get_active(patient)
        return {
            'id': str(patient.id),
            'full_name': patient.get_full_name(),
            'blood_group': patient.blood_group,
            'status': patient.status,
            'is_primary': patient.is_primary,
            'mobility_level': patient.mobility_level,
            'requires_wheelchair': patient.requires_wheelchair,
            'requires_oxygen': patient.requires_oxygen,
            'latest_vital': {
                'heart_rate': latest_vital.heart_rate,
                'blood_pressure': (
                    f"{latest_vital.blood_pressure_systolic}/{latest_vital.blood_pressure_diastolic}"
                    if latest_vital and latest_vital.blood_pressure_systolic else None
                ),
                'oxygen_saturation': latest_vital.oxygen_saturation if latest_vital else None,
                'recorded_at': latest_vital.recorded_at.isoformat() if latest_vital else None,
            } if latest_vital else None,
            'has_insurance': active_insurance is not None,
            'insurance_provider': active_insurance.provider_name if active_insurance else None,
        }

    @staticmethod
    def get_family_patients_summary(family_profile):
        patients = PatientRepository.get_by_family_profile(family_profile)
        return [PatientSelector.get_patient_summary(p) for p in patients]
