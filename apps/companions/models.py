"""Companions models — CompanionProfile, CompanionSkill, CompanionAvailability."""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from . import constants

User = get_user_model()


class CompanionProfile(models.Model):
    """
    Extended profile for a user with role=COMPANION.
    Stores professional details, location, ratings, and AI trust score.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='companion_profile',
    )

    # Professional info
    bio = models.TextField(blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    languages_spoken = models.JSONField(default=list)
    certifications = models.JSONField(default=list, help_text='List of certification names')

    # Vehicle
    vehicle_type = models.CharField(
        max_length=10,
        choices=constants.VEHICLE_CHOICES,
        default=constants.VEHICLE_NONE,
    )
    vehicle_number = models.CharField(max_length=20, blank=True)

    # Status & availability
    status = models.CharField(
        max_length=25,
        choices=constants.COMPANION_STATUS_CHOICES,
        default=constants.STATUS_PENDING_VERIFICATION,
        db_index=True,
    )
    availability_status = models.CharField(
        max_length=15,
        choices=constants.AVAILABILITY_CHOICES,
        default=constants.AVAILABILITY_OFFLINE,
        db_index=True,
    )

    # Current location (updated via live tracking)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)

    # Ratings & AI scores
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    total_bookings_completed = models.PositiveIntegerField(default=0)
    ai_trust_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # Bank details (for payouts)
    bank_account_number = models.CharField(max_length=20, blank=True)
    bank_ifsc = models.CharField(max_length=15, blank=True)
    bank_account_name = models.CharField(max_length=200, blank=True)
    upi_id = models.CharField(max_length=100, blank=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companion_profiles'
        verbose_name = 'Companion Profile'
        verbose_name_plural = 'Companion Profiles'
        indexes = [
            models.Index(fields=['status', 'availability_status']),
            models.Index(fields=['ai_trust_score']),
            models.Index(fields=['average_rating']),
        ]

    def __str__(self):
        return f"Companion — {self.user.get_full_name()} [{self.status}]"

    @property
    def computed_experience_years(self):
        from django.utils import timezone
        delta = timezone.now() - self.user.created_at
        return max(0.0, delta.total_seconds() / (365.25 * 24 * 3600))


class CompanionSkill(models.Model):
    """Skills associated with a companion profile."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    companion = models.ForeignKey(
        CompanionProfile, on_delete=models.CASCADE,
        related_name='skills', db_index=True,
    )
    skill = models.CharField(max_length=25, choices=constants.SKILL_CHOICES, db_index=True)
    proficiency_level = models.PositiveSmallIntegerField(
        default=1,
        help_text='1=Beginner, 2=Intermediate, 3=Expert',
    )
    verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'companion_skills'
        unique_together = [('companion', 'skill')]
        verbose_name = 'Companion Skill'

    def __str__(self):
        return f"{self.companion.user.get_full_name()} — {self.skill}"


class CompanionAvailabilitySlot(models.Model):
    """Weekly recurring availability slots for a companion."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    companion = models.ForeignKey(
        CompanionProfile, on_delete=models.CASCADE,
        related_name='availability_slots', db_index=True,
    )
    day_of_week = models.PositiveSmallIntegerField(
        help_text='0=Monday … 6=Sunday',
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'companion_availability_slots'
        verbose_name = 'Availability Slot'
        ordering = ['day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['companion', 'day_of_week']),
        ]

    def __str__(self):
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return f"{self.companion.user.get_full_name()} — {days[self.day_of_week]} {self.start_time}–{self.end_time}"
