"""Custom exceptions for the Patients module."""
from common.exceptions import (
    ResourceNotFoundException,
    BusinessLogicException,
    PermissionDeniedException,
    ConflictException,
)


class PatientNotFoundException(ResourceNotFoundException):
    default_detail = 'Patient not found.'
    default_code = 'patient_not_found'


class PatientLimitExceededException(BusinessLogicException):
    default_detail = 'Maximum patients per family limit reached.'
    default_code = 'patient_limit_exceeded'


class VitalNotFoundException(ResourceNotFoundException):
    default_detail = 'Vital record not found.'
    default_code = 'vital_not_found'


class InsuranceNotFoundException(ResourceNotFoundException):
    default_detail = 'Insurance record not found.'
    default_code = 'insurance_not_found'


class InsuranceAlreadyExistsException(ConflictException):
    default_detail = 'Active insurance already exists for this patient.'
    default_code = 'insurance_already_exists'


class PatientAccessDeniedException(PermissionDeniedException):
    default_detail = 'You do not have permission to access this patient.'
    default_code = 'patient_access_denied'


class NoFamilyProfileException(BusinessLogicException):
    default_detail = 'Family profile not found for this user.'
    default_code = 'no_family_profile'
