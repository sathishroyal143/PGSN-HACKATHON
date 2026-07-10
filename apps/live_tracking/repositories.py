"""Live Tracking repositories — all database queries live here."""
import logging
from django.utils import timezone
from .models import LocationUpdate, Route, Geofence, GeofenceEvent
from . import constants

logger = logging.getLogger('carebridge')


class LocationUpdateRepository:

    @staticmethod
    def create(booking, companion, validated_data: dict) -> LocationUpdate:
        return LocationUpdate.objects.create(
            booking=booking,
            companion=companion,
            **validated_data,
        )

    @staticmethod
    def get_latest_for_booking(booking_id) -> LocationUpdate | None:
        return (
            LocationUpdate.objects
            .filter(booking_id=booking_id)
            .order_by('-recorded_at')
            .first()
        )

    @staticmethod
    def get_history_for_booking(booking_id, limit: int = 500):
        return (
            LocationUpdate.objects
            .filter(booking_id=booking_id)
            .order_by('recorded_at')
            .values('latitude', 'longitude', 'speed', 'heading', 'recorded_at')[:limit]
        )

    @staticmethod
    def get_latest_for_companion(companion_id) -> LocationUpdate | None:
        return (
            LocationUpdate.objects
            .filter(companion_id=companion_id)
            .order_by('-recorded_at')
            .first()
        )


class RouteRepository:

    @staticmethod
    def create(booking, data: dict) -> Route:
        return Route.objects.create(booking=booking, **data)

    @staticmethod
    def get_active_route(booking_id) -> Route | None:
        return (
            Route.objects
            .filter(booking_id=booking_id, status=constants.ROUTE_STATUS_ACTIVE)
            .first()
        )

    @staticmethod
    def get_by_id(route_id) -> Route | None:
        return Route.objects.filter(id=route_id).first()

    @staticmethod
    def get_routes_for_booking(booking_id):
        return Route.objects.filter(booking_id=booking_id).order_by('created_at')

    @staticmethod
    def activate(route: Route) -> Route:
        # Deactivate any other active routes for the same booking
        Route.objects.filter(
            booking_id=route.booking_id,
            status=constants.ROUTE_STATUS_ACTIVE,
        ).exclude(id=route.id).update(status=constants.ROUTE_STATUS_CANCELLED)

        route.status = constants.ROUTE_STATUS_ACTIVE
        route.started_at = timezone.now()
        route.save(update_fields=['status', 'started_at', 'updated_at'])
        return route

    @staticmethod
    def complete(route: Route) -> Route:
        route.status = constants.ROUTE_STATUS_COMPLETED
        route.completed_at = timezone.now()
        route.actual_arrival = timezone.now()
        route.save(update_fields=['status', 'completed_at', 'actual_arrival', 'updated_at'])
        return route

    @staticmethod
    def update_eta(route: Route, estimated_arrival) -> Route:
        route.estimated_arrival = estimated_arrival
        route.save(update_fields=['estimated_arrival', 'updated_at'])
        return route


class GeofenceRepository:

    @staticmethod
    def create(booking, data: dict) -> Geofence:
        return Geofence.objects.create(booking=booking, **data)

    @staticmethod
    def get_active_for_booking(booking_id):
        return Geofence.objects.filter(booking_id=booking_id, is_active=True)

    @staticmethod
    def get_by_id(geofence_id) -> Geofence | None:
        return Geofence.objects.filter(id=geofence_id).first()

    @staticmethod
    def deactivate(geofence: Geofence) -> Geofence:
        geofence.is_active = False
        geofence.save(update_fields=['is_active', 'updated_at'])
        return geofence


class GeofenceEventRepository:

    @staticmethod
    def create(geofence: Geofence, booking, companion, event_type: str, lat, lng) -> GeofenceEvent:
        return GeofenceEvent.objects.create(
            geofence=geofence,
            booking=booking,
            companion=companion,
            event_type=event_type,
            latitude=lat,
            longitude=lng,
            occurred_at=timezone.now(),
        )

    @staticmethod
    def get_events_for_booking(booking_id):
        return (
            GeofenceEvent.objects
            .filter(booking_id=booking_id)
            .select_related('geofence')
            .order_by('-occurred_at')
        )

    @staticmethod
    def has_entered(booking_id, fence_type: str) -> bool:
        return GeofenceEvent.objects.filter(
            booking_id=booking_id,
            geofence__fence_type=fence_type,
            event_type=constants.GEOFENCE_EVENT_ENTER,
        ).exists()
