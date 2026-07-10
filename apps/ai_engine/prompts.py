"""AI Engine prompt templates for OpenAI / Azure OpenAI."""

MEDICAL_SUMMARY_SYSTEM = (
    "You are a clinical assistant. Generate a concise, plain-English medical summary "
    "for a care companion. Be factual, avoid jargon, and keep it under 150 words."
)


def medical_summary_prompt(patient_data: dict) -> str:
    name = patient_data.get('name', 'Patient')
    age = patient_data.get('age')
    gender = patient_data.get('gender', 'Not specified')
    blood_group = patient_data.get('blood_group', 'Not specified')
    
    mobility_level = patient_data.get('mobility_level', 'Not specified')
    requires_wheelchair = "Yes" if patient_data.get('requires_wheelchair') else "No"
    requires_oxygen = "Yes" if patient_data.get('requires_oxygen') else "No"
    requires_stretcher = "Yes" if patient_data.get('requires_stretcher') else "No"
    
    known_allergies = patient_data.get('known_allergies') or 'None reported'
    chronic_conditions = patient_data.get('chronic_conditions') or 'None reported'
    current_medications = patient_data.get('current_medications') or 'None reported'
    special_needs = patient_data.get('special_needs') or 'None reported'
    dietary_restrictions = patient_data.get('dietary_restrictions') or 'None reported'
    emergency_notes = patient_data.get('emergency_notes') or 'None reported'
    
    recent_diagnoses = ', '.join(patient_data.get('recent_diagnoses', [])) or 'None reported'
    recent_prescriptions = ', '.join(patient_data.get('recent_prescriptions', [])) or 'None reported'
    
    vitals = patient_data.get('recent_vitals', {})
    vitals_str = ', '.join(
        f"{k.replace('_', ' ')}: {v}" for k, v in vitals.items()
    ) if vitals else 'Not provided'

    return (
        f"Patient: {name}" + (f", Age {age}" if age else "") + f", Gender: {gender}, Blood Group: {blood_group}\n"
        f"Mobility: {mobility_level} (Wheelchair: {requires_wheelchair}, Oxygen: {requires_oxygen}, Stretcher: {requires_stretcher})\n\n"
        f"--- Patient Profile ---\n"
        f"Known Allergies: {known_allergies}\n"
        f"Chronic Conditions: {chronic_conditions}\n"
        f"Current Medications: {current_medications}\n"
        f"Special Needs: {special_needs}\n"
        f"Dietary Restrictions: {dietary_restrictions}\n"
        f"Emergency Notes: {emergency_notes}\n\n"
        f"--- Recent Medical Records ---\n"
        f"Recent Diagnoses: {recent_diagnoses}\n"
        f"Recent Prescriptions: {recent_prescriptions}\n"
        f"Recent Vitals: {vitals_str}\n\n"
        "Please write a comprehensive, yet concise plain-English medical summary for a care companion using all the detailed profile information above."
    )


PRIORITY_SYSTEM = (
    "You are a triage assistant. Based on the patient information provided, "
    "assess the care priority level: low, medium, high, or emergency. "
    "Respond with JSON: {\"priority_level\": \"...\", \"reason\": \"...\"}."
)


def priority_prompt(patient_age, conditions, is_emergency, vitals):
    conditions_str = ', '.join(conditions) if conditions else 'None'
    vitals_str = str(vitals) if vitals else 'Not provided'
    return (
        f"Patient age: {patient_age or 'Unknown'}\n"
        f"Conditions: {conditions_str}\n"
        f"Emergency flag: {is_emergency}\n"
        f"Vitals: {vitals_str}\n"
        "Assess care priority."
    )
