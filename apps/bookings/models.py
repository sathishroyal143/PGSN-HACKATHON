"""Bookings models — Booking, BookingStatusLog."""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.patients.models import Patient
from apps.services.models import ServicePackage, CareService
from . import constants

User = get_user_model()


class Booking(models.Model):
    """
    Core booking record.
    A family books a ServicePackage for a Patient.
    A Companion is assigned (manually or via AI matching).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Parties
    family_user = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='bookings_as_family', db_index=True,
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT,
        related_name='bookings', db_index=True,
    )
    companion = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='bookings_as_companion', db_index=True,
    )

    # Service — one of care_service OR service_package must be set
    care_service = models.ForeignKey(
        CareService, on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='bookings', db_index=True,
    )
    service_package = models.ForeignKey(
        ServicePackage, on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='bookings', db_index=True,
    )
    # Snapshot of the service name at booking time (survives service deletion)
    service_name = models.CharField(max_length=255, blank=True, default='')

    # Booking details
    booking_type = models.CharField(
        max_length=15,
        choices=constants.BOOKING_TYPE_CHOICES,
        default=constants.BOOKING_TYPE_SCHEDULED,
        db_index=True,
    )
    status = models.CharField(
        max_length=25,
        choices=constants.BOOKING_STATUS_CHOICES,
        default=constants.STATUS_PENDING,
        db_index=True,
    )

    # Schedule
    scheduled_start = models.DateTimeField(db_index=True)
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)

    # Location
    pickup_address = models.TextField()
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    hospital_name = models.CharField(max_length=255, blank=True)
    hospital_address = models.TextField(blank=True)
    hospital_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    hospital_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Pricing snapshot (captured at booking time)
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_breakdown = models.JSONField(default=dict)

    # Special requirements
    special_instructions = models.TextField(blank=True)
    requires_wheelchair = models.BooleanField(default=False)
    requires_oxygen = models.BooleanField(default=False)

    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.CharField(
        max_length=15,
        choices=constants.CANCEL_BY_CHOICES,
        blank=True,
    )
    cancellation_reason = models.TextField(blank=True)

    # AI matching score
    ai_match_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['family_user', 'status']),
            models.Index(fields=['companion', 'status']),
            models.Index(fields=['scheduled_start']),
            models.Index(fields=['status', 'booking_type']),
        ]

    def __str__(self):
        return f"Booking {self.id} — {self.patient.get_full_name()} [{self.status}]"

    @property
    def duration_hours(self):
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return round(delta.total_seconds() / 3600, 2)
        delta = self.scheduled_end - self.scheduled_start
        return round(delta.total_seconds() / 3600, 2)


class BookingStatusLog(models.Model):
    """Immutable audit trail of every status transition for a booking."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE,
        related_name='status_logs', db_index=True,
    )
    from_status = models.CharField(max_length=25, blank=True)
    to_status = models.CharField(max_length=25, choices=constants.BOOKING_STATUS_CHOICES)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'booking_status_logs'
        verbose_name = 'Booking Status Log'
        verbose_name_plural = 'Booking Status Logs'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['booking', 'created_at']),
        ]

    def __str__(self):
        return f"{self.booking_id} | {self.from_status} → {self.to_status}"
