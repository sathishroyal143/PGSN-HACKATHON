from django.contrib import admin
from .models import MedicalRecord, Prescription, LabReport, RecordDocument


class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 0
    fields = ['medicine_name', 'dosage', 'frequency', 'status', 'prescribed_date']


class LabReportInline(admin.TabularInline):
    model = LabReport
    extra = 0
    fields = ['test_name', 'lab_name', 'test_date', 'status']


class RecordDocumentInline(admin.TabularInline):
    model = RecordDocument
    extra = 0
    fields = ['original_filename', 'document_type', 'file_size_kb', 'uploaded_by']
    readonly_fields = ['original_filename', 'document_type', 'file_size_kb', 'uploaded_by']


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'record_type', 'patient', 'hospital_name', 'record_date', 'is_deleted']
    list_filter = ['record_type', 'is_deleted', 'record_date']
    search_fields = ['title', 'patient__first_name', 'patient__last_name', 'hospital_name', 'doctor_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'ai_summary']
    inlines = [PrescriptionInline, LabReportInline, RecordDocumentInline]
    date_hierarchy = 'record_date'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['medicine_name', 'dosage', 'frequency', 'status', 'prescribed_date']
    list_filter = ['status', 'frequency']
    search_fields = ['medicine_name', 'medical_record__title']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'lab_name', 'test_date', 'status']
    list_filter = ['status']
    search_fields = ['test_name', 'lab_name', 'medical_record__title']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(RecordDocument)
class RecordDocumentAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'document_type', 'file_size_kb', 'uploaded_by', 'created_at']
    list_filter = ['document_type']
    search_fields = ['original_filename', 'medical_record__title']
    readonly_fields = ['id', 'created_at']
