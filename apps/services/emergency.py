"""
Emergency Care helpers.

Emergency Care handles critical emergency situations.
Features: highest priority, immediate companion assignment,
emergency hospital recommendation, emergency escalation,
live tracking integration, emergency contact notification.
"""

from django.conf import settings
from .repositories import CareServiceRepository
from . import constants


def get_emergency_services():
    """Return all active Emergency Care services."""
    return CareServiceRepository.get_by_category_code(constants.CATEGORY_CODE_EMERGENCY)


def get_emergency_response_time_minutes() -> int:
    """Return the target emergency response time in minutes."""
    return getattr(settings, 'EMERGENCY_RESPONSE_TIME_MINUTES', 15)


def calculate_emergency_price(base_price: float) -> float:
    """
    Apply the emergency surcharge to a base price.
    Returns the adjusted price including the emergency surcharge.
    """
    surcharge_pct = constants.EMERGENCY_SURCHARGE_DEFAULT_PCT
    return round(base_price * (1 + surcharge_pct / 100), 2)


def get_emergency_priority() -> int:
    """Return the booking priority level for Emergency Care (highest = 1)."""
    return constants.CARE_MODE_PRIORITY[constants.CARE_MODE_EMERGENCY]


def is_emergency_service(service) -> bool:
    """Return True if the service is an Emergency Care service."""
    return (
        service.emergency_supported
        and service.service_category.code == constants.CATEGORY_CODE_EMERGENCY
    )
