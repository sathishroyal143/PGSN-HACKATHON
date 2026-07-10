"""Live Tracking selectors — read-only query helpers."""
from django.utils import timezone
from datetime import timedelta
from .models import LocationUpdate, Route, Geofence, GeofenceEvent
from .repositories import LocationUpdateRepository, RouteRepository, GeofenceRepository, GeofenceEventRepository
from . import constants


class TrackingSelectors:

    @staticmethod
    def get_live_location(booking_id) -> dict | None:
        update = LocationUpdateRepository.get_latest_for_booking(booking_id)
        if not update:
            return None
        stale_threshold = timezone.now() - timedelta(seconds=constants.LOCATION_STALE_SECONDS)
        return {
            'latitude': float(update.latitude),
            'longitude': float(update.longitude),
            'speed': update.speed,
            'heading': update.heading,
            'accuracy': update.accuracy,
            'recorded_at': update.recorded_at.isoformat(),
            'is_stale': update.recorded_at < stale_threshold,
        }

    @staticmethod
    def get_location_history(booking_id, limit: int = 500) -> list:
        qs = LocationUpdateRepository.get_history_for_booking(booking_id, limit)
        return [
            {
                'latitude': float(r['latitude']),
                'longitude': float(r['longitude']),
                'speed': r['speed'],
                'heading': r['heading'],
                'recorded_at': r['recorded_at'].isoformat(),
            }
            for r in qs
        ]

    @staticmethod
    def get_active_route(booking_id) -> Route | None:
        return RouteRepository.get_active_route(booking_id)

    @staticmethod
    def get_all_routes(booking_id):
        return RouteRepository.get_routes_for_booking(booking_id)

    @staticmethod
    def get_active_geofences(booking_id):
        return GeofenceRepository.get_active_for_booking(booking_id)

    @staticmethod
    def get_geofence_events(booking_id):
        return GeofenceEventRepository.get_events_for_booking(booking_id)

    @staticmethod
    def get_tracking_summary(booking_id) -> dict:
        live = TrackingSelectors.get_live_location(booking_id)
        active_route = RouteRepository.get_active_route(booking_id)
        geofences = list(
            GeofenceRepository.get_active_for_booking(booking_id)
            .values('id', 'fence_type', 'name', 'latitude', 'longitude', 'radius_meters')
        )
        return {
            'live_location': live,
            'active_route': {
                'id': str(active_route.id),
                'leg': active_route.leg,
                'status': active_route.status,
                'estimated_arrival': active_route.estimated_arrival.isoformat() if active_route.estimated_arrival else None,
                'distance_meters': active_route.distance_meters,
                'duration_seconds': active_route.duration_seconds,
            } if active_route else None,
            'geofences': geofences,
        }
