"""Priority engine — rule-based care priority assessment."""
from . import constants


def assess_priority(patient_age=None, conditions=None, is_emergency=False, vitals=None, patient_data=None):
    """
    Returns a priority level string and a score (0–100).
    conditions: list of condition strings
    vitals: dict with keys like heart_rate, blood_pressure_systolic, spo2
    patient_data: dict with mobility and condition details
    """
    score = 0
    conditions = conditions or []
    vitals = vitals or {}
    patient_data = patient_data or {}

    if is_emergency:
        return constants.PRIORITY_EMERGENCY, 100

    # Age factor
    if patient_age:
        if patient_age >= 80:
            score += 30
        elif patient_age >= 65:
            score += 20
        elif patient_age <= 5:
            score += 15

    # Condition keywords
    high_risk = {'cancer', 'cardiac', 'stroke', 'diabetes', 'dementia', 'alzheimer', 'parkinson'}
    matched_conditions = sum(1 for c in conditions if any(k in c.lower() for k in high_risk))
    
    chronic = patient_data.get('chronic_conditions', '').lower()
    matched_chronic = sum(1 for k in high_risk if k in chronic)
    
    score += min((matched_conditions + matched_chronic) * 15, 30)

    # Mobility & Equipment
    mobility = patient_data.get('mobility_level', '').upper()
    if mobility == 'BEDRIDDEN':
        score += 25
    elif mobility == 'ASSISTED':
        score += 10
        
    if patient_data.get('requires_oxygen'):
        score += 25
    if patient_data.get('requires_stretcher'):
        score += 20
    if patient_data.get('requires_wheelchair'):
        score += 10
        
    # Emergency Notes
    if patient_data.get('emergency_notes'):
        score += 15

    # Vitals
    spo2 = vitals.get('spo2')
    hr = vitals.get('heart_rate')
    bp = vitals.get('blood_pressure_systolic')

    if spo2 and spo2 < 90:
        score += 30
    elif spo2 and spo2 < 95:
        score += 15

    if hr and (hr > 120 or hr < 50):
        score += 20
    if bp and (bp > 180 or bp < 80):
        score += 20

    score = min(score, 99)

    if score >= 70:
        level = constants.PRIORITY_HIGH
    elif score >= 40:
        level = constants.PRIORITY_MEDIUM
    else:
        level = constants.PRIORITY_LOW

    return level, score
