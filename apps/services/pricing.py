"""
Care Services pricing helpers.
Provides price breakdown calculations for CareService records.
Legacy ServicePricing.calculate_total() handles ServicePackage pricing.
"""

from decimal import Decimal, ROUND_HALF_UP
from . import constants


def calculate_care_service_price(
    base_price: Decimal,
    hours: float = 1.0,
    is_emergency: bool = False,
    is_instant: bool = False,
    is_night: bool = False,
    gst_pct: float = constants.GST_DEFAULT_PCT,
    platform_commission_pct: float = constants.PLATFORM_COMMISSION_DEFAULT_PCT,
) -> dict:
    """
    Calculate a full price breakdown for a CareService booking.

    Args:
        base_price: Base price per hour in INR.
        hours: Number of service hours.
        is_emergency: Apply emergency surcharge.
        is_instant: Apply instant care surcharge.
        is_night: Apply night surcharge (10 PM – 6 AM).
        gst_pct: GST percentage to apply.
        platform_commission_pct: Platform commission percentage.

    Returns:
        dict with base_price, surcharges, gst, platform_commission, and total.
    """
    h = Decimal(str(hours))
    bp = Decimal(str(base_price))
    subtotal = bp * h

    emergency_surcharge = (
        subtotal * Decimal(str(constants.EMERGENCY_SURCHARGE_DEFAULT_PCT)) / Decimal('100')
        if is_emergency else Decimal('0')
    )
    instant_surcharge = (
        subtotal * Decimal(str(constants.INSTANT_SURCHARGE_DEFAULT_PCT)) / Decimal('100')
        if is_instant else Decimal('0')
    )
    night_surcharge = (
        subtotal * Decimal(str(constants.NIGHT_SURCHARGE_DEFAULT_PCT)) / Decimal('100')
        if is_night else Decimal('0')
    )

    adjusted = subtotal + emergency_surcharge + instant_surcharge + night_surcharge
    commission = adjusted * Decimal(str(platform_commission_pct)) / Decimal('100')
    gst = adjusted * Decimal(str(gst_pct)) / Decimal('100')
    total = adjusted + gst

    def _r(v: Decimal) -> float:
        return float(v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    return {
        'base_price': _r(subtotal),
        'emergency_surcharge': _r(emergency_surcharge),
        'instant_surcharge': _r(instant_surcharge),
        'night_surcharge': _r(night_surcharge),
        'adjusted_subtotal': _r(adjusted),
        'platform_commission': _r(commission),
        'gst': _r(gst),
        'total': _r(total),
    }
