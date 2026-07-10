# Record types
RECORD_TYPE_CONSULTATION = 'CONSULTATION'
RECORD_TYPE_LAB_REPORT = 'LAB_REPORT'
RECORD_TYPE_PRESCRIPTION = 'PRESCRIPTION'
RECORD_TYPE_IMAGING = 'IMAGING'
RECORD_TYPE_DISCHARGE = 'DISCHARGE'
RECORD_TYPE_VACCINATION = 'VACCINATION'
RECORD_TYPE_SURGERY = 'SURGERY'
RECORD_TYPE_OTHER = 'OTHER'

RECORD_TYPE_CHOICES = [
    (RECORD_TYPE_CONSULTATION, 'Consultation'),
    (RECORD_TYPE_LAB_REPORT, 'Lab Report'),
    (RECORD_TYPE_PRESCRIPTION, 'Prescription'),
    (RECORD_TYPE_IMAGING, 'Imaging / Radiology'),
    (RECORD_TYPE_DISCHARGE, 'Discharge Summary'),
    (RECORD_TYPE_VACCINATION, 'Vaccination'),
    (RECORD_TYPE_SURGERY, 'Surgery / Procedure'),
    (RECORD_TYPE_OTHER, 'Other'),
]

# Document types
DOC_TYPE_PDF = 'PDF'
DOC_TYPE_IMAGE = 'IMAGE'
DOC_TYPE_OTHER = 'OTHER'

DOCUMENT_TYPE_CHOICES = [
    (DOC_TYPE_PDF, 'PDF'),
    (DOC_TYPE_IMAGE, 'Image'),
    (DOC_TYPE_OTHER, 'Other'),
]

# Prescription status
PRESCRIPTION_ACTIVE = 'ACTIVE'
PRESCRIPTION_COMPLETED = 'COMPLETED'
PRESCRIPTION_CANCELLED = 'CANCELLED'

PRESCRIPTION_STATUS_CHOICES = [
    (PRESCRIPTION_ACTIVE, 'Active'),
    (PRESCRIPTION_COMPLETED, 'Completed'),
    (PRESCRIPTION_CANCELLED, 'Cancelled'),
]

# Frequency choices
FREQ_ONCE_DAILY = 'ONCE_DAILY'
FREQ_TWICE_DAILY = 'TWICE_DAILY'
FREQ_THRICE_DAILY = 'THRICE_DAILY'
FREQ_FOUR_TIMES = 'FOUR_TIMES'
FREQ_AS_NEEDED = 'AS_NEEDED'
FREQ_WEEKLY = 'WEEKLY'
FREQ_OTHER = 'OTHER'

FREQUENCY_CHOICES = [
    (FREQ_ONCE_DAILY, 'Once Daily'),
    (FREQ_TWICE_DAILY, 'Twice Daily'),
    (FREQ_THRICE_DAILY, 'Thrice Daily'),
    (FREQ_FOUR_TIMES, 'Four Times Daily'),
    (FREQ_AS_NEEDED, 'As Needed'),
    (FREQ_WEEKLY, 'Weekly'),
    (FREQ_OTHER, 'Other'),
]

# Lab report status
LAB_PENDING = 'PENDING'
LAB_COMPLETED = 'COMPLETED'
LAB_ABNORMAL = 'ABNORMAL'

LAB_STATUS_CHOICES = [
    (LAB_PENDING, 'Pending'),
    (LAB_COMPLETED, 'Completed'),
    (LAB_ABNORMAL, 'Abnormal'),
]

# Limits
MAX_DOCUMENTS_PER_RECORD = 10
MAX_FILE_SIZE_MB = 20

# Messages
MSG_RECORD_CREATED = 'Medical record created successfully.'
MSG_RECORD_UPDATED = 'Medical record updated successfully.'
MSG_RECORD_DELETED = 'Medical record deleted successfully.'
MSG_PRESCRIPTION_CREATED = 'Prescription created successfully.'
MSG_PRESCRIPTION_UPDATED = 'Prescription updated successfully.'
MSG_PRESCRIPTION_DELETED = 'Prescription deleted successfully.'
MSG_LAB_REPORT_CREATED = 'Lab report created successfully.'
MSG_LAB_REPORT_UPDATED = 'Lab report updated successfully.'
MSG_LAB_REPORT_DELETED = 'Lab report deleted successfully.'
MSG_DOCUMENT_UPLOADED = 'Document uploaded successfully.'
MSG_DOCUMENT_DELETED = 'Document deleted successfully.'

# Error messages
ERR_RECORD_NOT_FOUND = 'Medical record not found.'
ERR_PRESCRIPTION_NOT_FOUND = 'Prescription not found.'
ERR_LAB_REPORT_NOT_FOUND = 'Lab report not found.'
ERR_DOCUMENT_NOT_FOUND = 'Document not found.'
ERR_ACCESS_DENIED = 'You do not have access to this medical record.'
ERR_DOC_LIMIT = f'Maximum {MAX_DOCUMENTS_PER_RECORD} documents allowed per record.'
ERR_FILE_TOO_LARGE = f'File size must not exceed {MAX_FILE_SIZE_MB}MB.'
