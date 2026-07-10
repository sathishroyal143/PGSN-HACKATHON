from common.exceptions import ResourceNotFoundException, PermissionDeniedException, BusinessLogicException


class MedicalRecordNotFoundException(ResourceNotFoundException):
    default_detail = 'Medical record not found.'
    default_code = 'medical_record_not_found'


class PrescriptionNotFoundException(ResourceNotFoundException):
    default_detail = 'Prescription not found.'
    default_code = 'prescription_not_found'


class LabReportNotFoundException(ResourceNotFoundException):
    default_detail = 'Lab report not found.'
    default_code = 'lab_report_not_found'


class DocumentNotFoundException(ResourceNotFoundException):
    default_detail = 'Document not found.'
    default_code = 'document_not_found'


class MedicalRecordAccessDeniedException(PermissionDeniedException):
    default_detail = 'You do not have access to this medical record.'
    default_code = 'medical_record_access_denied'


class DocumentLimitExceededException(BusinessLogicException):
    default_detail = 'Maximum documents per record exceeded.'
    default_code = 'document_limit_exceeded'


class FileTooLargeException(BusinessLogicException):
    default_detail = 'File size exceeds the allowed limit.'
    default_code = 'file_too_large'
