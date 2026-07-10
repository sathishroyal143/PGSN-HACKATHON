"""Medical summary generator — tries Azure OpenAI → OpenAI → rule-based fallback."""
import logging
from .exceptions import OpenAIUnavailableException
from .prompts import MEDICAL_SUMMARY_SYSTEM, medical_summary_prompt

logger = logging.getLogger('carebridge')


def generate_summary(patient_data: dict) -> str:
    """
    Generate a plain-text medical summary.
    Tries Azure OpenAI first, then OpenAI, then falls back to rule-based.
    """
    prompt = medical_summary_prompt(patient_data)

    # Try Azure OpenAI
    try:
        from .azure_openai import chat_completion as azure_chat
        return azure_chat(MEDICAL_SUMMARY_SYSTEM, prompt)
    except OpenAIUnavailableException:
        pass

    # Try OpenAI
    try:
        from .openai_client import chat_completion as openai_chat
        return openai_chat(MEDICAL_SUMMARY_SYSTEM, prompt)
    except OpenAIUnavailableException:
        pass

    # Rule-based fallback
    logger.info('medical_summary: using rule-based fallback')
    return _rule_based_summary(patient_data)


def _rule_based_summary(patient_data: dict) -> str:
    lines = []
    name = patient_data.get('name', 'Patient')
    age = patient_data.get('age')
    gender = patient_data.get('gender', 'Not specified')
    blood_group = patient_data.get('blood_group', 'Not specified')
    mobility = patient_data.get('mobility_level', 'Not specified')
    requires_wheelchair = "Yes" if patient_data.get('requires_wheelchair') else "No"
    requires_oxygen = "Yes" if patient_data.get('requires_oxygen') else "No"
    requires_stretcher = "Yes" if patient_data.get('requires_stretcher') else "No"
    
    lines.append(f"Patient: {name} (Age: {age or 'N/A'}, Gender: {gender}, Blood Group: {blood_group})")
    lines.append(f"Mobility: {mobility} (Wheelchair: {requires_wheelchair}, Oxygen: {requires_oxygen}, Stretcher: {requires_stretcher})")
    
    if patient_data.get('known_allergies'):
        lines.append("Known Allergies: " + patient_data.get('known_allergies'))
    if patient_data.get('chronic_conditions'):
        lines.append("Chronic Conditions: " + patient_data.get('chronic_conditions'))
    if patient_data.get('current_medications'):
        lines.append("Current Medications (Profile): " + patient_data.get('current_medications'))
    if patient_data.get('special_needs'):
        lines.append("Special Needs: " + patient_data.get('special_needs'))
    if patient_data.get('dietary_restrictions'):
        lines.append("Dietary Restrictions: " + patient_data.get('dietary_restrictions'))
    if patient_data.get('emergency_notes'):
        lines.append("Emergency Notes: " + patient_data.get('emergency_notes'))

    recent_diagnoses = patient_data.get('recent_diagnoses', [])
    if recent_diagnoses:
        lines.append("Recent Diagnoses: " + ", ".join(recent_diagnoses))
        
    recent_prescriptions = patient_data.get('recent_prescriptions', [])
    if recent_prescriptions:
        lines.append("Recent Prescriptions: " + ", ".join(recent_prescriptions))

    vitals = patient_data.get('recent_vitals', {})
    if vitals:
        parts = []
        if vitals.get('heart_rate'):
            parts.append(f"HR {vitals['heart_rate']} bpm")
        if vitals.get('blood_pressure_systolic') and vitals.get('blood_pressure_diastolic'):
            parts.append(f"BP {vitals['blood_pressure_systolic']}/{vitals['blood_pressure_diastolic']} mmHg")
        if vitals.get('spo2'):
            parts.append(f"SpO2 {vitals['spo2']}%")
        if vitals.get('temperature'):
            parts.append(f"Temp {vitals['temperature']}°C")
        if parts:
            lines.append("Recent Vitals: " + ", ".join(parts))

    return "\n".join(lines)
