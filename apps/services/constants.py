"""
Care Services constants.
Defines all choices, codes, and configuration values for the services module.
"""

# ── Service Type Codes (legacy — kept for backward compatibility) ──────────────

SERVICE_TYPE_HOSPITAL_VISIT = 'HOSPITAL_VISIT'
SERVICE_TYPE_HOME_CARE = 'HOME_CARE'
SERVICE_TYPE_EMERGENCY = 'EMERGENCY'
SERVICE_TYPE_DIAGNOSTIC = 'DIAGNOSTIC'
SERVICE_TYPE_PHARMACY = 'PHARMACY'
SERVICE_TYPE_PHYSIOTHERAPY = 'PHYSIOTHERAPY'
SERVICE_TYPE_NURSING = 'NURSING'

SERVICE_TYPE_CHOICES = [
    (SERVICE_TYPE_HOSPITAL_VISIT, 'Hospital Visit'),
    (SERVICE_TYPE_HOME_CARE, 'Home Care'),
    (SERVICE_TYPE_EMERGENCY, 'Emergency'),
    (SERVICE_TYPE_DIAGNOSTIC, 'Diagnostic'),
    (SERVICE_TYPE_PHARMACY, 'Pharmacy Run'),
    (SERVICE_TYPE_PHYSIOTHERAPY, 'Physiotherapy'),
    (SERVICE_TYPE_NURSING, 'Nursing'),
]

# ── Care Mode Codes ────────────────────────────────────────────────────────────

CARE_MODE_SCHEDULED = 'SCHEDULED'
CARE_MODE_INSTANT = 'INSTANT'
CARE_MODE_EMERGENCY = 'EMERGENCY'

CARE_MODE_CHOICES = [
    (CARE_MODE_SCHEDULED, 'Scheduled Care'),
    (CARE_MODE_INSTANT, 'Instant Care'),
    (CARE_MODE_EMERGENCY, 'Emergency Care'),
]

CARE_MODE_PRIORITY = {
    CARE_MODE_SCHEDULED: 3,
    CARE_MODE_INSTANT: 2,
    CARE_MODE_EMERGENCY: 1,
}

# ── Pricing Types ──────────────────────────────────────────────────────────────

PRICING_TYPE_HOURLY = 'HOURLY'
PRICING_TYPE_FIXED = 'FIXED'
PRICING_TYPE_PACKAGE = 'PACKAGE'

PRICING_TYPE_CHOICES = [
    (PRICING_TYPE_HOURLY, 'Hourly'),
    (PRICING_TYPE_FIXED, 'Fixed'),
    (PRICING_TYPE_PACKAGE, 'Package'),
]

# ── Status ─────────────────────────────────────────────────────────────────────

STATUS_ACTIVE = 'ACTIVE'
STATUS_INACTIVE = 'INACTIVE'
STATUS_DRAFT = 'DRAFT'

STATUS_CHOICES = [
    (STATUS_ACTIVE, 'Active'),
    (STATUS_INACTIVE, 'Inactive'),
    (STATUS_DRAFT, 'Draft'),
]

# ── Service Category Codes ─────────────────────────────────────────────────────

CATEGORY_CODE_SCHEDULED = 'SCHEDULED_CARE'
CATEGORY_CODE_INSTANT = 'INSTANT_CARE'
CATEGORY_CODE_EMERGENCY = 'EMERGENCY_CARE'

CATEGORY_CODE_CHOICES = [
    (CATEGORY_CODE_SCHEDULED, 'Scheduled Care'),
    (CATEGORY_CODE_INSTANT, 'Instant Care'),
    (CATEGORY_CODE_EMERGENCY, 'Emergency Care'),
]

# ── Business Rules ─────────────────────────────────────────────────────────────

MIN_DURATION_MINUTES = 30
MAX_DURATION_HOURS = 24
MIN_BASE_PRICE = 0
MAX_BASE_PRICE = 999999

EMERGENCY_SURCHARGE_DEFAULT_PCT = 50
INSTANT_SURCHARGE_DEFAULT_PCT = 20
NIGHT_SURCHARGE_DEFAULT_PCT = 20
PLATFORM_COMMISSION_DEFAULT_PCT = 15
GST_DEFAULT_PCT = 18

# ── Search ─────────────────────────────────────────────────────────────────────

SEARCH_MIN_LENGTH = 2
SEARCH_MAX_RESULTS = 50
