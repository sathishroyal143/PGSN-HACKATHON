"""
Patient models for CareBridge-AI.

Patient        — core patient profile linked to a FamilyMember.
PatientVital   — periodic vital sign recordings.
PatientInsurance — insurance details per patient.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.family.models import FamilyProfile, FamilyMember
from . import constants


class Patient(models.Model):
    """
    Core patient profile.
    Each FamilyMember who needs care is represented as a Patient.
    One-to-one with FamilyMember.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family_profile = models.ForeignKey(
        FamilyProfile,
        on_delete=models.CASCADE,
        related_name='patients',
        db_index=True,
    )
    family_member = models.OneToOneField(
        FamilyMember,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        null=True,
        blank=True,
    )

    # Demographics (denormalized for quick access during bookings)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=constants.GENDER_CHOICES,
        blank=True,
    )
    blood_group = models.CharField(
        max_length=10,
        choices=constants.BLOOD_GROUP_CHOICES,
        default=constants.BLOOD_GROUP_UNKNOWN,
    )

    # Medical quick-reference
    known_allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    special_needs = models.TextField(blank=True)
    dietary_restrictions = models.TextField(blank=True)

    # Mobility & assistance
    mobility_level = models.CharField(
        max_length=20,
        choices=constants.MOBILITY_CHOICES,
        default=constants.MOBILITY_INDEPENDENT,
    )
    requires_wheelchair = models.BooleanField(default=False)
    requires_oxygen = models.BooleanField(default=False)
    requires_stretcher = models.BooleanField(default=False)

    # Emergency info
    emergency_notes = models.TextField(blank=True)

    # Preferences
    preferred_doctor_name = models.CharField(max_length=255, blank=True)
    preferred_hospital_name = models.CharField(max_length=255, blank=True)
    preferred_hospital_address = models.TextField(blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=constants.STATUS_CHOICES,
        default=constants.STATUS_ACTIVE,
        db_index=True,
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Primary patient for this family account.',
    )

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['-is_primary', 'first_name']
        indexes = [
            models.Index(fields=['family_profile', 'is_deleted']),
            models.Index(fields=['status']),
            models.Index(fields=['is_primary']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.blood_group})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        from django.utils import timezone
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class PatientVital(models.Model):
    """
    Periodic vital sign recordings for a patient.
    Recorded by companion or family before/after a care journey.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='vitals',
        db_index=True,
    )

    # Vitals
    blood_pressure_systolic = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(300)],
        help_text='Systolic BP in mmHg',
    )
    blood_pressure_diastolic = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        help_text='Diastolic BP in mmHg',
    )
    heart_rate = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(20), MaxValueValidator(300)],
        help_text='Heart rate in bpm',
    )
    temperature = models.DecimalField(
        max_digits=4, decimal_places=1,
        null=True, blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(45)],
        help_text='Body temperature in °C',
    )
    oxygen_saturation = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(100)],
        help_text='SpO2 percentage',
    )
    blood_glucose = models.DecimalField(
        max_digits=5, decimal_places=1,
        null=True, blank=True,
        help_text='Blood glucose in mg/dL',
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text='Weight in kg',
    )
    height = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text='Height in cm',
    )

    notes = models.TextField(blank=True)
    recorded_by = models.CharField(max_length=200, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'patient_vitals'
        verbose_name = 'Patient Vital'
        verbose_name_plural = 'Patient Vitals'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['patient', 'recorded_at']),
        ]

    def __str__(self):
        return f"Vitals — {self.patient.get_full_name()} @ {self.recorded_at:%Y-%m-%d %H:%M}"

    @property
    def bmi(self):
        if self.weight and self.height and self.height > 0:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 1)
        return None


class PatientInsurance(models.Model):
    """
    Insurance details for a patient.
    Only one active insurance record per patient at a time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='insurance_records',
        db_index=True,
    )

    insurance_type = models.CharField(
        max_length=20,
        choices=constants.INSURANCE_TYPE_CHOICES,
        default=constants.INSURANCE_NONE,
    )
    provider_name = models.CharField(max_length=200, blank=True)
    policy_number = models.CharField(max_length=100, blank=True)
    policy_holder_name = models.CharField(max_length=200, blank=True)
    coverage_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text='Coverage amount in INR',
    )
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patient_insurance'
        verbose_name = 'Patient Insurance'
        verbose_name_plural = 'Patient Insurance Records'
        ordering = ['-is_active', '-created_at']
        indexes = [
            models.Index(fields=['patient', 'is_active']),
        ]

    def __str__(self):
        return f"{self.provider_name or 'No Insurance'} — {self.patient.get_full_name()}"
