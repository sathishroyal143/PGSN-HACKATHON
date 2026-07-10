"""
Scheduled Care helpers.

Scheduled Care allows advance booking for planned healthcare visits.
Features: preferred date/time, home/hospital visit, companion preference,
estimated duration, service pricing.
"""

from datetime import date, timedelta
from django.conf import settings
from .repositories import CareServiceRepository
from . import constants


def get_scheduled_services():
    """Return all active Scheduled Care services."""
    return CareServiceRepository.get_by_category_code(constants.CATEGORY_CODE_SCHEDULED)


def get_max_advance_booking_date() -> date:
    """Return the latest date a scheduled booking can be placed."""
    max_days = getattr(settings, 'MAX_BOOKING_ADVANCE_DAYS', 30)
    return date.today() + timedelta(days=max_days)


def validate_scheduled_date(preferred_date: date) -> bool:
    """
    Return True if preferred_date is valid for a scheduled booking.
    Must be today or in the future, and within the advance booking window.
    """
    today = date.today()
    return today <= preferred_date <= get_max_advance_booking_date()


def supports_home_visit(service) -> bool:
    """Return True if the given CareService supports home visits."""
    return service.home_visit_supported


def supports_hospital_visit(service) -> bool:
    """Return True if the given CareService supports hospital visits."""
    return service.hospital_visit_supported
