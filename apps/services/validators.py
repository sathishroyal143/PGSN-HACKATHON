"""
Validators for the Care Services module.
Field-level validation functions used by serializers and service layer.
"""

from decimal import Decimal
from typing import Optional
from . import constants
from .exceptions import InvalidPriceException, InvalidDurationException


def validate_base_price(value: Decimal) -> Decimal:
    """Ensure base_price is non-negative."""
    if value is None:
        raise InvalidPriceException('Price is required.')
    if value < Decimal('0'):
        raise InvalidPriceException()
    return value


def validate_non_negative_money(value: Optional[Decimal], field_name: str) -> Optional[Decimal]:
    """Ensure optional money fields are not negative."""
    if value is not None and value < Decimal('0'):
        raise InvalidPriceException(f'{field_name} cannot be negative.')
    return value


def validate_duration(value: int) -> int:
    """Ensure estimated_duration is positive and within allowed bounds."""
    if value is None:
        raise InvalidDurationException('Duration is required.')
    if value < constants.MIN_DURATION_MINUTES:
        raise InvalidDurationException(
            f'Duration must be at least {constants.MIN_DURATION_MINUTES} minutes.'
        )
    max_minutes = constants.MAX_DURATION_HOURS * 60
    if value > max_minutes:
        raise InvalidDurationException(
            f'Duration cannot exceed {constants.MAX_DURATION_HOURS} hours ({max_minutes} minutes).'
        )
    return value


def validate_service_code(value: str) -> str:
    """Ensure service_code is uppercase alphanumeric with underscores only."""
    import re
    if not re.match(r'^[A-Z0-9_]+$', value):
        from common.exceptions import ValidationException
        raise ValidationException('Service code must be uppercase letters, digits, and underscores only.')
    return value
