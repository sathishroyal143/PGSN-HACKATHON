"""Care Journey models — CareJourney, JourneyStep."""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.bookings.models import Booking
from . import constants

User = get_user_model()


class CareJourney(models.Model):
    """
    Tracks the real-time progress of a booking through all care steps.
    One journey per booking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE,
        related_name='care_journey',
    )
    status = models.CharField(
        max_length=15,
        choices=constants.JOURNEY_STATUS_CHOICES,
        default=constants.JOURNEY_STATUS_ACTIVE,
        db_index=True,
    )
    current_step = models.CharField(
        max_length=25,
        choices=constants.JOURNEY_STEPS,
        default=constants.STEP_ACCEPTED,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Companion notes for the family
    companion_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'care_journeys'
        verbose_name = 'Care Journey'
        verbose_name_plural = 'Care Journeys'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['booking']),
        ]

    def __str__(self):
        return f"Journey {self.id} — Booking {self.booking_id} [{self.status}]"


class JourneyStep(models.Model):
    """
    Individual step within a CareJourney.
    Created automatically when a journey starts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journey = models.ForeignKey(
        CareJourney, on_delete=models.CASCADE,
        related_name='steps', db_index=True,
    )
    step_code = models.CharField(max_length=25, choices=constants.JOURNEY_STEPS)
    step_order = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=15,
        choices=constants.STEP_STATUS_CHOICES,
        default=constants.STEP_STATUS_PENDING,
        db_index=True,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    family_notified = models.BooleanField(default=False)

    class Meta:
        db_table = 'journey_steps'
        verbose_name = 'Journey Step'
        verbose_name_plural = 'Journey Steps'
        ordering = ['step_order']
        unique_together = [('journey', 'step_code')]
        indexes = [
            models.Index(fields=['journey', 'step_order']),
        ]

    def __str__(self):
        return f"{self.journey_id} — {self.step_code} [{self.status}]"


class JourneyMedia(models.Model):
    """
    Stores uploaded files (images, reports, bills, prescriptions) per journey step.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    step = models.ForeignKey(
        JourneyStep, on_delete=models.CASCADE, related_name='media', db_index=True
    )
    file = models.FileField(upload_to='journey_media/')
    file_type = models.CharField(
        max_length=50, blank=True,
        help_text="e.g. 'Prescription', 'Bill', 'Report', 'Image'"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'journey_media'
        verbose_name = 'Journey Media'
        verbose_name_plural = 'Journey Media'

    def __str__(self):
        return f"{self.file_type or 'Media'} for Step {self.step_id}"
