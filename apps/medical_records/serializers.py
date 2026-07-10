"""Serializers for Medical Records module."""
from rest_framework import serializers
from .models import MedicalRecord, Prescription, LabReport, RecordDocument
from . import constants


class RecordDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordDocument
        fields = ['id', 'file', 'original_filename', 'document_type', 'file_size_kb', 'uploaded_by', 'created_at']
        read_only_fields = ['id', 'original_filename', 'document_type', 'file_size_kb', 'uploaded_by', 'created_at']


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = [
            'id', 'medicine_name', 'dosage', 'frequency', 'duration_days',
            'instructions', 'status', 'prescribed_date', 'end_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        prescribed = data.get('prescribed_date')
        end = data.get('end_date')
        if prescribed and end and end < prescribed:
            raise serializers.ValidationError('end_date must be on or after prescribed_date.')
        return data


class LabReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = [
            'id', 'test_name', 'lab_name', 'test_date', 'result_value',
            'reference_range', 'unit', 'status', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = [
            'record_type', 'title', 'description', 'hospital_name',
            'doctor_name', 'doctor_specialization', 'diagnosis',
            'treatment_notes', 'follow_up_date', 'record_date',
        ]

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Title cannot be blank.')
        return value.strip()


class MedicalRecordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = [
            'record_type', 'title', 'description', 'hospital_name',
            'doctor_name', 'doctor_specialization', 'diagnosis',
            'treatment_notes', 'follow_up_date', 'record_date',
        ]


class MedicalRecordListSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'record_type', 'title', 'hospital_name', 'doctor_name',
            'record_date', 'patient_name', 'created_at',
        ]

    def get_patient_name(self, obj):
        return obj.patient.get_full_name()


class MedicalRecordDetailSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    lab_reports = LabReportSerializer(many=True, read_only=True)
    documents = RecordDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'record_type', 'title', 'description', 'hospital_name',
            'doctor_name', 'doctor_specialization', 'diagnosis',
            'treatment_notes', 'follow_up_date', 'record_date',
            'ai_summary', 'patient_name', 'prescriptions', 'lab_reports',
            'documents', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'ai_summary', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name()


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'doc', 'docx'}

    def validate_file(self, value):
        max_bytes = constants.MAX_FILE_SIZE_MB * 1024 * 1024
        if value.size > max_bytes:
            raise serializers.ValidationError(constants.ERR_FILE_TOO_LARGE)
        ext = value.name.rsplit('.', 1)[-1].lower() if '.' in value.name else ''
        if ext not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            )
        return value
