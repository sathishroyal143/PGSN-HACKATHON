"""
Medical Records models.

MedicalRecord  — core health event (consultation, discharge, etc.)
Prescription   — medication prescribed during a record
LabReport      — lab/diagnostic test result linked to a record
RecordDocument — file attachments (PDF/image) for any record
"""
import uuid
from django.db import models
from apps.patients.models import Patient
from . import constants


class MedicalRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_records',
        db_index=True,
    )

    record_type = models.CharField(
        max_length=20,
        choices=constants.RECORD_TYPE_CHOICES,
        default=constants.RECORD_TYPE_CONSULTATION,
        db_index=True,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Clinical details
    hospital_name = models.CharField(max_length=255, blank=True)
    doctor_name = models.CharField(max_length=255, blank=True)
    doctor_specialization = models.CharField(max_length=100, blank=True)
    diagnosis = models.TextField(blank=True)
    treatment_notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    record_date = models.DateField(db_index=True)

    # AI-generated summary (populated asynchronously)
    ai_summary = models.TextField(blank=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medical_records'
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'
        ordering = ['-record_date', '-created_at']
        indexes = [
            models.Index(fields=['patient', 'is_deleted']),
            models.Index(fields=['record_type', 'record_date']),
        ]

    def __str__(self):
        return f"{self.title} — {self.patient.get_full_name()} ({self.record_date})"


class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        db_index=True,
    )

    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(
        max_length=20,
        choices=constants.FREQUENCY_CHOICES,
        default=constants.FREQ_ONCE_DAILY,
    )
    duration_days = models.PositiveSmallIntegerField(null=True, blank=True)
    instructions = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=constants.PRESCRIPTION_STATUS_CHOICES,
        default=constants.PRESCRIPTION_ACTIVE,
        db_index=True,
    )
    prescribed_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prescriptions'
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-prescribed_date']
        indexes = [
            models.Index(fields=['medical_record', 'status']),
        ]

    def __str__(self):
        return f"{self.medicine_name} ({self.dosage}) — {self.status}"


class LabReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='lab_reports',
        db_index=True,
    )

    test_name = models.CharField(max_length=255)
    lab_name = models.CharField(max_length=255, blank=True)
    test_date = models.DateField()
    result_value = models.CharField(max_length=255, blank=True)
    reference_range = models.CharField(max_length=255, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    status = models.CharField(
        max_length=20,
        choices=constants.LAB_STATUS_CHOICES,
        default=constants.LAB_PENDING,
        db_index=True,
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lab_reports'
        verbose_name = 'Lab Report'
        verbose_name_plural = 'Lab Reports'
        ordering = ['-test_date']
        indexes = [
            models.Index(fields=['medical_record', 'status']),
        ]

    def __str__(self):
        return f"{self.test_name} — {self.status} ({self.test_date})"


class RecordDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='documents',
        db_index=True,
    )

    file = models.FileField(upload_to='medical_records/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=10,
        choices=constants.DOCUMENT_TYPE_CHOICES,
        default=constants.DOC_TYPE_PDF,
    )
    file_size_kb = models.PositiveIntegerField(default=0)
    uploaded_by = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'record_documents'
        verbose_name = 'Record Document'
        verbose_name_plural = 'Record Documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['medical_record']),
        ]

    def __str__(self):
        return f"{self.original_filename} — {self.medical_record.title}"
