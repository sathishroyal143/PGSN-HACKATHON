"""
Custom exceptions for the Care Services module.
All exceptions extend CareBridgeBaseException for consistent error handling.
"""

from common.exceptions import (
    CareBridgeBaseException,
    ResourceNotFoundException,
    ValidationException,
    BusinessLogicException,
    ConflictException,
)


class ServiceCategoryNotFoundException(ResourceNotFoundException):
    """Raised when a ServiceCategory is not found."""
    default_detail = 'Service category not found.'
    default_code = 'service_category_not_found'


class CareServiceNotFoundException(ResourceNotFoundException):
    """Raised when a CareService is not found."""
    default_detail = 'Care service not found.'
    default_code = 'care_service_not_found'


class ServicePricingNotFoundException(ResourceNotFoundException):
    """Raised when ServicePricing is not found for a service."""
    default_detail = 'Service pricing not found.'
    default_code = 'service_pricing_not_found'


class DuplicateServiceNameException(ConflictException):
    """Raised when a CareService with the same name already exists."""
    default_detail = 'A service with this name already exists.'
    default_code = 'duplicate_service_name'


class DuplicateServiceCodeException(ConflictException):
    """Raised when a CareService with the same code already exists."""
    default_detail = 'A service with this code already exists.'
    default_code = 'duplicate_service_code'


class DuplicateCategoryCodeException(ConflictException):
    """Raised when a ServiceCategory with the same code already exists."""
    default_detail = 'A category with this code already exists.'
    default_code = 'duplicate_category_code'


class InvalidPriceException(ValidationException):
    """Raised when a price value is negative or invalid."""
    default_detail = 'Price cannot be negative.'
    default_code = 'invalid_price'


class InvalidDurationException(ValidationException):
    """Raised when a duration value is zero or negative."""
    default_detail = 'Duration must be a positive value.'
    default_code = 'invalid_duration'


class ServiceInactiveException(BusinessLogicException):
    """Raised when attempting to book or interact with an inactive service."""
    default_detail = 'This service is currently inactive.'
    default_code = 'service_inactive'


class ServiceNotBookableException(BusinessLogicException):
    """Raised when a service does not support the requested visit type."""
    default_detail = 'This service does not support the requested visit type.'
    default_code = 'service_not_bookable'


__all__ = [
    'ServiceCategoryNotFoundException',
    'CareServiceNotFoundException',
    'ServicePricingNotFoundException',
    'DuplicateServiceNameException',
    'DuplicateServiceCodeException',
    'DuplicateCategoryCodeException',
    'InvalidPriceException',
    'InvalidDurationException',
    'ServiceInactiveException',
    'ServiceNotBookableException',
]
