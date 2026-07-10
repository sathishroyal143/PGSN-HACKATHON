"""Repository layer — reusable DB queries for Medical Records."""
from django.db import transaction
from django.utils import timezone
from .models import MedicalRecord, Prescription, LabReport, RecordDocument


class MedicalRecordRepository:

    @staticmethod
    def get_by_id(record_id):
        try:
            return MedicalRecord.objects.select_related('patient').get(
                id=record_id, is_deleted=False
            )
        except MedicalRecord.DoesNotExist:
            return None

    @staticmethod
    def get_by_patient(patient, record_type=None):
        qs = MedicalRecord.objects.filter(patient=patient, is_deleted=False)
        if record_type:
            qs = qs.filter(record_type=record_type)
        return qs.order_by('-record_date', '-created_at')

    @staticmethod
    def get_all(filters=None):
        qs = MedicalRecord.objects.filter(is_deleted=False).select_related('patient')
        if filters:
            qs = qs.filter(**filters)
        return qs.order_by('-record_date')

    @staticmethod
    @transaction.atomic
    def create(data):
        return MedicalRecord.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(record, data):
        for field, value in data.items():
            setattr(record, field, value)
        record.save()
        return record

    @staticmethod
    @transaction.atomic
    def soft_delete(record):
        record.is_deleted = True
        record.deleted_at = timezone.now()
        record.save(update_fields=['is_deleted', 'deleted_at'])


class PrescriptionRepository:

    @staticmethod
    def get_by_id(prescription_id):
        try:
            return Prescription.objects.select_related('medical_record').get(id=prescription_id)
        except Prescription.DoesNotExist:
            return None

    @staticmethod
    def get_by_record(medical_record):
        return Prescription.objects.filter(medical_record=medical_record).order_by('-prescribed_date')

    @staticmethod
    def get_active_by_patient(patient):
        from . import constants
        return Prescription.objects.filter(
            medical_record__patient=patient,
            medical_record__is_deleted=False,
            status=constants.PRESCRIPTION_ACTIVE,
        ).select_related('medical_record').order_by('-prescribed_date')

    @staticmethod
    @transaction.atomic
    def create(data):
        return Prescription.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(prescription, data):
        for field, value in data.items():
            setattr(prescription, field, value)
        prescription.save()
        return prescription

    @staticmethod
    @transaction.atomic
    def delete(prescription):
        prescription.delete()


class LabReportRepository:

    @staticmethod
    def get_by_id(report_id):
        try:
            return LabReport.objects.select_related('medical_record').get(id=report_id)
        except LabReport.DoesNotExist:
            return None

    @staticmethod
    def get_by_record(medical_record):
        return LabReport.objects.filter(medical_record=medical_record).order_by('-test_date')

    @staticmethod
    @transaction.atomic
    def create(data):
        return LabReport.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(report, data):
        for field, value in data.items():
            setattr(report, field, value)
        report.save()
        return report

    @staticmethod
    @transaction.atomic
    def delete(report):
        report.delete()


class RecordDocumentRepository:

    @staticmethod
    def get_by_id(doc_id):
        try:
            return RecordDocument.objects.select_related('medical_record').get(id=doc_id)
        except RecordDocument.DoesNotExist:
            return None

    @staticmethod
    def get_by_record(medical_record):
        return RecordDocument.objects.filter(medical_record=medical_record).order_by('-created_at')

    @staticmethod
    def count_by_record(medical_record):
        return RecordDocument.objects.filter(medical_record=medical_record).count()

    @staticmethod
    @transaction.atomic
    def create(data):
        return RecordDocument.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def delete(document):
        document.file.delete(save=False)
        document.delete()
