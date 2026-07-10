"""Live Tracking models — LocationUpdate, Route, Geofence, GeofenceEvent."""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.bookings.models import Booking
from . import constants

User = get_user_model()


class LocationUpdate(models.Model):
    """
    Stores every GPS ping from a companion during an active booking.
    High-frequency writes — indexed on booking + timestamp for efficient
    time-series queries.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE,
        related_name='location_updates', db_index=True,
    )
    companion = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='location_updates', db_index=True,
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy = models.FloatField(
        null=True, blank=True,
        help_text='GPS accuracy in meters',
    )
    speed = models.FloatField(
        null=True, blank=True,
        help_text='Speed in km/h',
    )
    heading = models.FloatField(
        null=True, blank=True,
        help_text='Compass heading in degrees (0–360)',
    )
    altitude = models.FloatField(null=True, blank=True)
    source = models.CharField(
        max_length=20,
        choices=constants.SOURCE_CHOICES,
        default=constants.SOURCE_COMPANION_APP,
    )
    recorded_at = models.DateTimeField(
        db_index=True,
        help_text='Device timestamp when GPS fix was taken',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'location_updates'
        verbose_name = 'Location Update'
        verbose_name_plural = 'Location Updates'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['booking', 'recorded_at']),
            models.Index(fields=['companion', 'recorded_at']),
        ]

    def __str__(self):
        return f"Location {self.companion_id} @ {self.recorded_at} ({self.latitude}, {self.longitude})"


class Route(models.Model):
    """
    Planned or active route for a booking.
    Stores the full polyline and per-leg ETA data.
    One booking can have at most one active route at a time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE,
        related_name='routes', db_index=True,
    )
    leg = models.CharField(
        max_length=10,
        choices=constants.LEG_TYPE_CHOICES,
        default=constants.LEG_PICKUP,
        db_index=True,
    )
    status = models.CharField(
        max_length=15,
        choices=constants.ROUTE_STATUS_CHOICES,
        default=constants.ROUTE_STATUS_PLANNED,
        db_index=True,
    )

    # Origin
    origin_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    origin_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    origin_address = models.TextField(blank=True)

    # Destination
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    destination_address = models.TextField(blank=True)

    # Route data from mapping API
    polyline = models.TextField(
        blank=True,
        help_text='Encoded polyline string (Google Maps format)',
    )
    distance_meters = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    # ETA
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'routes'
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['booking', 'leg', 'status']),
        ]

    def __str__(self):
        return f"Route {self.id} — Booking {self.booking_id} [{self.leg}] [{self.status}]"


class Geofence(models.Model):
    """
    Circular geofence zone associated with a booking.
    Used to trigger automatic journey step transitions when
    companion enters/exits a zone.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE,
        related_name='geofences', db_index=True,
    )
    fence_type = models.CharField(
        max_length=10,
        choices=constants.GEOFENCE_TYPE_CHOICES,
        db_index=True,
    )
    name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_meters = models.PositiveIntegerField(
        default=constants.DEFAULT_GEOFENCE_RADIUS_METERS,
    )
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'geofences'
        verbose_name = 'Geofence'
        verbose_name_plural = 'Geofences'
        indexes = [
            models.Index(fields=['booking', 'fence_type', 'is_active']),
        ]

    def __str__(self):
        return f"Geofence [{self.fence_type}] — {self.name} r={self.radius_meters}m"


class GeofenceEvent(models.Model):
    """
    Immutable log of every geofence enter/exit event.
    Drives automatic journey step progression.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geofence = models.ForeignKey(
        Geofence, on_delete=models.CASCADE,
        related_name='events', db_index=True,
    )
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE,
        related_name='geofence_events', db_index=True,
    )
    companion = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='geofence_events',
    )
    event_type = models.CharField(
        max_length=5,
        choices=constants.GEOFENCE_EVENT_CHOICES,
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    occurred_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'geofence_events'
        verbose_name = 'Geofence Event'
        verbose_name_plural = 'Geofence Events'
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['booking', 'occurred_at']),
            models.Index(fields=['geofence', 'event_type']),
        ]

    def __str__(self):
        return f"GeofenceEvent [{self.event_type}] — {self.geofence.name} @ {self.occurred_at}"
