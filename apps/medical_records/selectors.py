"""Selectors — read-only queries returning structured data."""
from .repositories import (
    MedicalRecordRepository, PrescriptionRepository,
    LabReportRepository, RecordDocumentRepository,
)
from . import constants


class MedicalRecordSelector:

    @staticmethod
    def get_patient_summary(patient):
        records = MedicalRecordRepository.get_by_patient(patient)
        active_prescriptions = PrescriptionRepository.get_active_by_patient(patient)
        return {
            'total_records': records.count(),
            'by_type': {
                rtype: records.filter(record_type=rtype).count()
                for rtype, _ in constants.RECORD_TYPE_CHOICES
            },
            'active_prescriptions': active_prescriptions.count(),
            'latest_record_date': records.values_list('record_date', flat=True).first(),
        }

    @staticmethod
    def get_timeline(patient):
        records = MedicalRecordRepository.get_by_patient(patient)
        return [
            {
                'id': str(r.id),
                'title': r.title,
                'record_type': r.record_type,
                'record_date': r.record_date,
                'hospital_name': r.hospital_name,
                'doctor_name': r.doctor_name,
            }
            for r in records
        ]
