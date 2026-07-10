"""Care reminder engine — generates medication and appointment reminders."""
from datetime import datetime, timedelta


def generate_medication_reminders(medications: list) -> list:
    """
    Given a list of medication dicts with 'name' and 'frequency',
    return a list of reminder message strings.
    frequency: 'daily', 'twice_daily', 'weekly'
    """
    reminders = []
    for med in medications:
        name = med.get('name', 'medication')
        freq = med.get('frequency', 'daily')
        if freq == 'twice_daily':
            reminders.append(f"Take {name} — Morning dose")
            reminders.append(f"Take {name} — Evening dose")
        elif freq == 'weekly':
            reminders.append(f"Take {name} — Weekly dose due")
        else:
            reminders.append(f"Take {name} — Daily dose")
    return reminders


def generate_appointment_reminder(appointment_dt: datetime, hospital: str = '', doctor: str = '') -> str:
    """Return a reminder string for an upcoming appointment."""
    now = datetime.now()
    delta = appointment_dt - now
    hours_away = int(delta.total_seconds() / 3600)

    parts = [f"Appointment in {hours_away} hour(s)"]
    if hospital:
        parts.append(f"at {hospital}")
    if doctor:
        parts.append(f"with {doctor}")
    return " ".join(parts)


def get_care_reminders(patient_data: dict) -> list:
    """
    Aggregate all reminders for a patient.
    patient_data keys: medications (list), next_appointment (ISO str), hospital, doctor
    """
    reminders = []

    meds = patient_data.get('medications', [])
    if meds:
        reminders.extend(generate_medication_reminders(meds))

    appt_str = patient_data.get('next_appointment')
    if appt_str:
        try:
            appt_dt = datetime.fromisoformat(appt_str)
            reminders.append(generate_appointment_reminder(
                appt_dt,
                hospital=patient_data.get('hospital', ''),
                doctor=patient_data.get('doctor', ''),
            ))
        except ValueError:
            pass

    return reminders
