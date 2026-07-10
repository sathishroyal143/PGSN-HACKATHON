"""
Views for Medical Records module.
Thin ViewSets — all business logic in services.
"""
import logging
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

from common.responses import (
    success_response, created_response, updated_response, deleted_response,
)
from apps.users.models import UserRole
from apps.patients.services import PatientService
from apps.patients.exceptions import PatientNotFoundException

from .exceptions import (
    MedicalRecordNotFoundException, PrescriptionNotFoundException,
    LabReportNotFoundException, DocumentNotFoundException,
    MedicalRecordAccessDeniedException,
)
from .permissions import IsFamilyOrAdmin
from .repositories import (
    MedicalRecordRepository, PrescriptionRepository,
    LabReportRepository, RecordDocumentRepository,
)
from .selectors import MedicalRecordSelector
from .serializers import (
    MedicalRecordCreateSerializer, MedicalRecordUpdateSerializer,
    MedicalRecordListSerializer, MedicalRecordDetailSerializer,
    PrescriptionSerializer, LabReportSerializer,
    RecordDocumentSerializer, DocumentUploadSerializer,
)
from .services import (
    MedicalRecordService, PrescriptionService,
    LabReportService, RecordDocumentService,
)
from . import constants

logger = logging.getLogger('carebridge')


def _get_family_profile(user):
    try:
        return user.family_profile
    except Exception:
        from apps.patients.exceptions import NoFamilyProfileException
        raise NoFamilyProfileException()


def _resolve_patient(request, patient_pk):
    """Fetch patient and enforce ownership for non-admin users."""
    patient = PatientService.get_patient_or_raise(patient_pk)
    if request.user.role != UserRole.ADMIN:
        family_profile = _get_family_profile(request.user)
        PatientService.assert_family_owns_patient(family_profile, patient)
    return patient


def _resolve_record(request, record_pk):
    """Fetch record and enforce ownership for non-admin users."""
    record = MedicalRecordService.get_record_or_raise(record_pk)
    if request.user.role != UserRole.ADMIN:
        family_profile = _get_family_profile(request.user)
        try:
            if record.patient.family_profile != family_profile:
                raise MedicalRecordAccessDeniedException()
        except Exception:
            raise MedicalRecordAccessDeniedException()
    return record


class MedicalRecordViewSet(ViewSet):
    """
    list        GET  /api/v1/medical-records/patients/{patient_pk}/records/
    create      POST /api/v1/medical-records/patients/{patient_pk}/records/
    retrieve    GET  /api/v1/medical-records/patients/{patient_pk}/records/{pk}/
    update      PUT  /api/v1/medical-records/patients/{patient_pk}/records/{pk}/
    partial_update PATCH ...
    destroy     DELETE ...
    summary     GET  /api/v1/medical-records/patients/{patient_pk}/records/summary/
    timeline    GET  /api/v1/medical-records/patients/{patient_pk}/records/timeline/
    """
    permission_classes = [IsAuthenticated, IsFamilyOrAdmin]

    def list(self, request, patient_pk=None):
        patient = _resolve_patient(request, patient_pk)
        record_type = request.query_params.get('record_type')
        records = MedicalRecordRepository.get_by_patient(patient, record_type=record_type)
        return success_response(
            data=MedicalRecordListSerializer(records, many=True).data,
            message='Medical records retrieved.',
        )

    def create(self, request, patient_pk=None):
        patient = _resolve_patient(request, patient_pk)
        serializer = MedicalRecordCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = MedicalRecordService.create_record(patient, serializer.validated_data)
        return created_response(
            data=MedicalRecordDetailSerializer(record).data,
            message=constants.MSG_RECORD_CREATED,
        )

    def retrieve(self, request, patient_pk=None, pk=None):
        patient = _resolve_patient(request, patient_pk)
        record = MedicalRecordService.get_record_or_raise(pk)
        MedicalRecordService.assert_patient_owns_record(patient, record)
        return success_response(
            data=MedicalRecordDetailSerializer(record).data,
            message='Medical record retrieved.',
        )

    def update(self, request, patient_pk=None, pk=None):
        patient = _resolve_patient(request, patient_pk)
        record = MedicalRecordService.get_record_or_raise(pk)
        MedicalRecordService.assert_patient_owns_record(patient, record)
        serializer = MedicalRecordUpdateSerializer(record, data=request.data)
        serializer.is_valid(raise_exception=True)
        record = MedicalRecordService.update_record(record, serializer.validated_data)
        return updated_response(
            data=MedicalRecordDetailSerializer(record).data,
            message=constants.MSG_RECORD_UPDATED,
        )

    def partial_update(self, request, patient_pk=None, pk=None):
        patient = _resolve_patient(request, patient_pk)
        record = MedicalRecordService.get_record_or_raise(pk)
        MedicalRecordService.assert_patient_owns_record(patient, record)
        serializer = MedicalRecordUpdateSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        record = MedicalRecordService.update_record(record, serializer.validated_data)
        return updated_response(
            data=MedicalRecordDetailSerializer(record).data,
            message=constants.MSG_RECORD_UPDATED,
        )

    def destroy(self, request, patient_pk=None, pk=None):
        patient = _resolve_patient(request, patient_pk)
        record = MedicalRecordService.get_record_or_raise(pk)
        MedicalRecordService.assert_patient_owns_record(patient, record)
        MedicalRecordService.delete_record(record)
        return deleted_response(message=constants.MSG_RECORD_DELETED)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request, patient_pk=None):
        patient = _resolve_patient(request, patient_pk)
        data = MedicalRecordSelector.get_patient_summary(patient)
        return success_response(data=data, message='Summary retrieved.')

    @action(detail=False, methods=['get'], url_path='timeline')
    def timeline(self, request, patient_pk=None):
        patient = _resolve_patient(request, patient_pk)
        data = MedicalRecordSelector.get_timeline(patient)
        return success_response(data=data, message='Timeline retrieved.')


class PrescriptionViewSet(ViewSet):
    """
    list    GET  /api/v1/medical-records/records/{record_pk}/prescriptions/
    create  POST ...
    update  PUT  .../prescriptions/{pk}/
    partial_update PATCH ...
    destroy DELETE ...
    """
    permission_classes = [IsAuthenticated, IsFamilyOrAdmin]

    def _get_record(self, request, record_pk):
        return _resolve_record(request, record_pk)

    def list(self, request, record_pk=None):
        record = self._get_record(request, record_pk)
        prescriptions = PrescriptionRepository.get_by_record(record)
        return success_response(
            data=PrescriptionSerializer(prescriptions, many=True).data,
            message='Prescriptions retrieved.',
        )

    def create(self, request, record_pk=None):
        record = self._get_record(request, record_pk)
        serializer = PrescriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prescription = PrescriptionService.create_prescription(record, serializer.validated_data)
        return created_response(
            data=PrescriptionSerializer(prescription).data,
            message=constants.MSG_PRESCRIPTION_CREATED,
        )

    def update(self, request, record_pk=None, pk=None):
        record = self._get_record(request, record_pk)
        prescription = PrescriptionService.get_prescription_or_raise(pk)
        if prescription.medical_record_id != record.id:
            raise PrescriptionNotFoundException()
        serializer = PrescriptionSerializer(prescription, data=request.data)
        serializer.is_valid(raise_exception=True)
        prescription = PrescriptionService.update_prescription(prescription, serializer.validated_data)
        return updated_response(
            data=PrescriptionSerializer(prescription).data,
            message=constants.MSG_PRESCRIPTION_UPDATED,
        )

    def partial_update(self, request, record_pk=None, pk=None):
        record = self._get_record(request, record_pk)
        prescription = PrescriptionService.get_prescription_or_raise(pk)
        if prescription.medical_record_id != record.id:
            raise PrescriptionNotFoundException()
        serializer = PrescriptionSerializer(prescription, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        prescription = PrescriptionService.update_prescription(prescription, serializer.validated_data)
        return updated_response(
            data=PrescriptionSerializer(prescription).data,
            message=constants.MSG_PRESCRIPTION_UPDATED,
        )

    def destroy(self, request, record_pk=None, pk=None):
        record = self._get_record(request, record_pk)
        PrescriptionService.delete_prescription(pk, record)
        return deleted_response(message=constants.MSG_PRESCRIPTION_DELETED)


class LabReportViewSet(ViewSet):
    """
    list    GET  /api/v1/medical-records/records/{record_pk}/lab-reports/
    create  POST ...
    update  PUT  .../lab-reports/{pk}/
    partial_update PATCH ...
    destroy DELETE ...
    """
    permission_classes = [IsAuthenticated, IsFamilyOrAdmin]

    def _get_record(self, request, record_pk):
        return _resolve_record(request, record_pk)

    def list(self, request, record_pk=None):
        record = self._get_record(request, record_pk)
        reports = LabReportRepository.get_by_record(record)
        return success_response(
            data=LabReportSerializer(reports, many=True).data,
            message='Lab reports retrieved.',
        )

    def create(self, request, record_pk=None):
        record = self._get_record(request, record_pk)
        serializer = LabReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = LabReportService.create_lab_report(record, serializer.validated_data)
        return created_response(
            data=LabReportSerializer(report).data,
            message=constants.MSG_LAB_REPORT_CREATED,
        )

    def update(self, request, record_pk=None, pk=None):
        record = self._get_record(request, record_pk)
        report = LabReportService.get_lab_report_or_raise(pk)
        if report.medical_record_id != record.id:
            raise LabReportNotFoundException()
        serializer = LabReportSerializer(report, data=request.data)
        serializer.is_valid(raise_exception=True)
        report = LabReportService.update_lab_report(report, serializer.validated_data)
        return updated_response(
            data=LabReportSerializer(report).data,
            message=constants.MSG_LAB_REPORT_UPDATED,
        )

    def partial_update(self, request, record_pk=None, pk=None):
        record = self._get_record(request, record_pk)
        report = LabReportService.get_lab_report_or_raise(pk)
        if report.medical_record_id != record.id:
            raise LabReportNotFoundException()
        serializer = LabReportSerializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        report = LabReportService.update_lab_report(report, serializer.validated_data)
        return updated_response(
            data=LabReportSerializer(report).data,
            message=constants.MSG_LAB_REPORT_UPDATED,
        )

    def destroy(self, request, record_pk=None, pk=None):
        record = self._get_record(request, record_pk)
        LabReportService.delete_lab_report(pk, record)
        return deleted_response(message=constants.MSG_LAB_REPORT_DELETED)


class RecordDocumentViewSet(ViewSet):
    """
    list    GET  /api/v1/medical-records/records/{record_pk}/documents/
    create  POST ... (multipart file upload)
    destroy DELETE .../documents/{pk}/
    """
    permission_classes = [IsAuthenticated, IsFamilyOrAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get_record(self, request, record_pk):
        return _resolve_record(request, record_pk)

    def list(self, request, record_pk=None):
        record = self._get_record(request, record_pk)
        documents = RecordDocumentRepository.get_by_record(record)
        return success_response(
            data=RecordDocumentSerializer(documents, many=True).data,
            message='Documents retrieved.',
        )

    def retrieve(self, request, record_pk=None, pk=None):
        record = self._get_record(request, record_pk)
        document = RecordDocumentRepository.get_by_id(pk)
        if not document or document.medical_record_id != record.id:
            raise DocumentNotFoundException()
        return success_response(
            data=RecordDocumentSerializer(document).data,
            message='Document retrieved.',
        )

    def create(self, request, record_pk=None):
        record = self._get_record(request, record_pk)
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = RecordDocumentService.upload_document(
            record,
            serializer.validated_data['file'],
            uploaded_by=request.user.get_full_name(),
        )
        return created_response(
            data=RecordDocumentSerializer(document).data,
            message=constants.MSG_DOCUMENT_UPLOADED,
        )

    def destroy(self, request, record_pk=None, pk=None):
        record = self._get_record(request, record_pk)
        RecordDocumentService.delete_document(pk, record)
        return deleted_response(message=constants.MSG_DOCUMENT_DELETED)
