"""Service layer — all business logic for Medical Records."""
import logging
from django.db import transaction
from .repositories import (
    MedicalRecordRepository, PrescriptionRepository,
    LabReportRepository, RecordDocumentRepository,
)
from .exceptions import (
    MedicalRecordNotFoundException, PrescriptionNotFoundException,
    LabReportNotFoundException, DocumentNotFoundException,
    MedicalRecordAccessDeniedException, DocumentLimitExceededException,
    FileTooLargeException,
)
from . import constants

logger = logging.getLogger('carebridge')


class MedicalRecordService:

    @staticmethod
    @transaction.atomic
    def create_record(patient, data):
        data['patient'] = patient
        record = MedicalRecordRepository.create(data)
        logger.info(f"MedicalRecord created: {record.id} for patient {patient.id}")
        return record

    @staticmethod
    @transaction.atomic
    def update_record(record, data):
        record = MedicalRecordRepository.update(record, data)
        logger.info(f"MedicalRecord updated: {record.id}")
        return record

    @staticmethod
    @transaction.atomic
    def delete_record(record):
        MedicalRecordRepository.soft_delete(record)
        logger.info(f"MedicalRecord soft-deleted: {record.id}")

    @staticmethod
    def get_record_or_raise(record_id):
        record = MedicalRecordRepository.get_by_id(record_id)
        if not record:
            raise MedicalRecordNotFoundException()
        return record

    @staticmethod
    def assert_patient_owns_record(patient, record):
        if record.patient_id != patient.id:
            raise MedicalRecordAccessDeniedException()


class PrescriptionService:

    @staticmethod
    @transaction.atomic
    def create_prescription(medical_record, data):
        data['medical_record'] = medical_record
        prescription = PrescriptionRepository.create(data)
        logger.info(f"Prescription created: {prescription.id}")
        return prescription

    @staticmethod
    @transaction.atomic
    def update_prescription(prescription, data):
        prescription = PrescriptionRepository.update(prescription, data)
        logger.info(f"Prescription updated: {prescription.id}")
        return prescription

    @staticmethod
    @transaction.atomic
    def delete_prescription(prescription_id, medical_record):
        prescription = PrescriptionRepository.get_by_id(prescription_id)
        if not prescription or prescription.medical_record_id != medical_record.id:
            raise PrescriptionNotFoundException()
        PrescriptionRepository.delete(prescription)
        logger.info(f"Prescription deleted: {prescription_id}")

    @staticmethod
    def get_prescription_or_raise(prescription_id):
        p = PrescriptionRepository.get_by_id(prescription_id)
        if not p:
            raise PrescriptionNotFoundException()
        return p


class LabReportService:

    @staticmethod
    @transaction.atomic
    def create_lab_report(medical_record, data):
        data['medical_record'] = medical_record
        report = LabReportRepository.create(data)
        logger.info(f"LabReport created: {report.id}")
        return report

    @staticmethod
    @transaction.atomic
    def update_lab_report(report, data):
        report = LabReportRepository.update(report, data)
        logger.info(f"LabReport updated: {report.id}")
        return report

    @staticmethod
    @transaction.atomic
    def delete_lab_report(report_id, medical_record):
        report = LabReportRepository.get_by_id(report_id)
        if not report or report.medical_record_id != medical_record.id:
            raise LabReportNotFoundException()
        LabReportRepository.delete(report)
        logger.info(f"LabReport deleted: {report_id}")

    @staticmethod
    def get_lab_report_or_raise(report_id):
        r = LabReportRepository.get_by_id(report_id)
        if not r:
            raise LabReportNotFoundException()
        return r


class RecordDocumentService:

    @staticmethod
    @transaction.atomic
    def upload_document(medical_record, file, uploaded_by=''):
        # Enforce document count limit
        count = RecordDocumentRepository.count_by_record(medical_record)
        if count >= constants.MAX_DOCUMENTS_PER_RECORD:
            raise DocumentLimitExceededException(constants.ERR_DOC_LIMIT)

        # Enforce file size limit
        max_bytes = constants.MAX_FILE_SIZE_MB * 1024 * 1024
        if file.size > max_bytes:
            raise FileTooLargeException(constants.ERR_FILE_TOO_LARGE)

        # Determine document type
        name = file.name.lower()
        if name.endswith('.pdf'):
            doc_type = constants.DOC_TYPE_PDF
        elif name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            doc_type = constants.DOC_TYPE_IMAGE
        else:
            doc_type = constants.DOC_TYPE_OTHER

        document = RecordDocumentRepository.create({
            'medical_record': medical_record,
            'file': file,
            'original_filename': file.name,
            'document_type': doc_type,
            'file_size_kb': file.size // 1024,
            'uploaded_by': uploaded_by,
        })
        logger.info(f"Document uploaded: {document.id} for record {medical_record.id}")
        return document

    @staticmethod
    @transaction.atomic
    def delete_document(doc_id, medical_record):
        document = RecordDocumentRepository.get_by_id(doc_id)
        if not document or document.medical_record_id != medical_record.id:
            raise DocumentNotFoundException()
        RecordDocumentRepository.delete(document)
        logger.info(f"Document deleted: {doc_id}")
