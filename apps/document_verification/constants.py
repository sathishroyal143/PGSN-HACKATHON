"""Constants for Document Verification module."""

# Document type
DOC_TYPE_AADHAR = 'aadhar'
DOC_TYPE_PAN = 'pan'
DOC_TYPE_PASSPORT = 'passport'
DOC_TYPE_DRIVING_LICENSE = 'driving_license'
DOC_TYPE_VOTER_ID = 'voter_id'
DOC_TYPE_POLICE_CLEARANCE = 'police_clearance'
DOC_TYPE_MEDICAL_CERT = 'medical_cert'
DOC_TYPE_TRAINING_CERT = 'training_cert'
DOC_TYPE_OTHER = 'other'

DOCUMENT_TYPE_CHOICES = [
    (DOC_TYPE_AADHAR, 'Aadhar Card'),
    (DOC_TYPE_PAN, 'PAN Card'),
    (DOC_TYPE_PASSPORT, 'Passport'),
    (DOC_TYPE_DRIVING_LICENSE, 'Driving License'),
    (DOC_TYPE_VOTER_ID, 'Voter ID'),
    (DOC_TYPE_POLICE_CLEARANCE, 'Police Clearance Certificate'),
    (DOC_TYPE_MEDICAL_CERT, 'Medical Certificate'),
    (DOC_TYPE_TRAINING_CERT, 'Training Certificate'),
    (DOC_TYPE_OTHER, 'Other'),
]

# Verification status
STATUS_PENDING = 'pending'
STATUS_UNDER_REVIEW = 'under_review'
STATUS_APPROVED = 'approved'
STATUS_REJECTED = 'rejected'
STATUS_EXPIRED = 'expired'

VERIFICATION_STATUS_CHOICES = [
    (STATUS_PENDING, 'Pending'),
    (STATUS_UNDER_REVIEW, 'Under Review'),
    (STATUS_APPROVED, 'Approved'),
    (STATUS_REJECTED, 'Rejected'),
    (STATUS_EXPIRED, 'Expired'),
]

# KYC status
KYC_STATUS_NOT_STARTED = 'not_started'
KYC_STATUS_IN_PROGRESS = 'in_progress'
KYC_STATUS_VERIFIED = 'verified'
KYC_STATUS_FAILED = 'failed'

KYC_STATUS_CHOICES = [
    (KYC_STATUS_NOT_STARTED, 'Not Started'),
    (KYC_STATUS_IN_PROGRESS, 'In Progress'),
    (KYC_STATUS_VERIFIED, 'Verified'),
    (KYC_STATUS_FAILED, 'Failed'),
]
