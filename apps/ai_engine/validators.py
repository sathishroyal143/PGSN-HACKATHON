"""AI Engine validators — reusable input validation helpers."""
from .exceptions import AIEngineException


def validate_uuid(value, field_name='id'):
    """Raise if value is falsy."""
    if not value:
        raise AIEngineException(f'{field_name} is required.')
    return value


def validate_top_n(value):
    """Clamp top_n between 1 and 20."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        return 10
    return max(1, min(n, 20))


def validate_hours(value, min_val=0.5, max_val=24.0):
    """Clamp hours to valid booking range."""
    try:
        h = float(value)
    except (TypeError, ValueError):
        return 1.0
    return max(min_val, min(h, max_val))


def validate_patient_data(data: dict):
    """Ensure minimum required fields for medical summary."""
    if not data.get('name', '').strip():
        raise AIEngineException('Patient name is required for medical summary.')
    return data
