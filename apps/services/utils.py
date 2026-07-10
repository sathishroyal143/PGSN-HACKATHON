"""
Utility helpers for the Care Services module.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from . import constants


def round_price(value: Decimal) -> Decimal:
    """Round a price to 2 decimal places using ROUND_HALF_UP."""
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def minutes_to_hours(minutes: int) -> float:
    """Convert minutes to hours, rounded to 2 decimal places."""
    return round(minutes / 60, 2)


def get_care_mode_priority(category_code: str) -> int:
    """
    Return the booking priority for a care mode code.
    Lower number = higher priority (Emergency=1, Instant=2, Scheduled=3).
    """
    mapping = {
        constants.CATEGORY_CODE_EMERGENCY: 1,
        constants.CATEGORY_CODE_INSTANT: 2,
        constants.CATEGORY_CODE_SCHEDULED: 3,
    }
    return mapping.get(category_code, 99)


def is_emergency_category(category_code: str) -> bool:
    """Return True if the category code represents Emergency Care."""
    return category_code == constants.CATEGORY_CODE_EMERGENCY


def is_instant_category(category_code: str) -> bool:
    """Return True if the category code represents Instant Care."""
    return category_code == constants.CATEGORY_CODE_INSTANT


def build_service_code(name: str, category_code: str) -> str:
    """
    Generate a deterministic service code from name and category.
    e.g. 'Blood Pressure Check' + 'SCHEDULED_CARE' → 'SCHEDULED_CARE_BLOOD_PRESSURE_CHECK'
    """
    import re
    slug = re.sub(r'[^A-Z0-9]+', '_', name.upper().strip())
    slug = slug.strip('_')
    return f"{category_code}_{slug}"
