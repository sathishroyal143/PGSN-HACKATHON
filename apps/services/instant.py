"""
Instant Care helpers.

Instant Care handles immediate care requests.
Features: nearby companion availability, estimated arrival time,
auto companion matching, dynamic pricing, live availability.
"""

from django.conf import settings
from .repositories import CareServiceRepository
from . import constants


def get_instant_services():
    """Return all active Instant Care services."""
    return CareServiceRepository.get_by_category_code(constants.CATEGORY_CODE_INSTANT)


def get_instant_booking_window_hours() -> int:
    """Return the number of hours within which an instant booking must be fulfilled."""
    return getattr(settings, 'INSTANT_BOOKING_WINDOW_HOURS', 4)


def calculate_instant_price(base_price: float) -> float:
    """
    Apply the instant care surcharge to a base price.
    Returns the adjusted price including the instant surcharge.
    """
    surcharge_pct = constants.INSTANT_SURCHARGE_DEFAULT_PCT
    return round(base_price * (1 + surcharge_pct / 100), 2)


def is_instant_available(service) -> bool:
    """
    Return True if the service is active and supports instant booking.
    Instant Care services must be in the INSTANT_CARE category and ACTIVE.
    """
    return (
        service.status == constants.STATUS_ACTIVE
        and not service.is_deleted
        and service.service_category.code == constants.CATEGORY_CODE_INSTANT
    )
