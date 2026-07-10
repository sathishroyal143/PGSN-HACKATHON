"""Live Tracking services — business logic layer."""
import logging
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from apps.bookings.models import Booking
from apps.companions.models import CompanionProfile
from .exceptions import (
    InvalidLocationException,
    TrackingNotActiveException,
    UnauthorizedTrackingAccessException,
)
from .geofence import is_inside_geofence
from .models import Geofence, GeofenceEvent, LocationUpdate, Route
from .repositories import (
    GeofenceEventRepository,
    GeofenceRepository,
    LocationUpdateRepository,
    RouteRepository,
)
from . import constants

logger = logging.getLogger('carebridge')


def _tracking_group(booking_id: str) -> str:
    return f"{constants.TRACKING_GROUP_PREFIX}{booking_id}"


def _broadcast(booking_id: str, message_type: str, payload: dict):
    """Send a message to all WebSocket clients watching this booking."""
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            _tracking_group(str(booking_id)),
            {'type': 'tracking.message', 'message_type': message_type, 'payload': payload},
        )
    except Exception as exc:
        logger.warning("Channel layer broadcast failed for booking %s: %s", booking_id, exc)


class LocationService:

    @staticmethod
    def record_location(booking: Booking, companion, data: dict) -> LocationUpdate:
        """
        Validate, persist a GPS ping, update companion's cached location,
        evaluate geofences, and broadcast to WebSocket subscribers.
        """
        lat = float(data['latitude'])
        lon = float(data['longitude'])

        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise InvalidLocationException('Coordinates out of valid range.')

        # Booking must be in an active state
        active_statuses = {'confirmed', 'in_progress'}
        if booking.status not in active_statuses:
            raise TrackingNotActiveException()

        # Companion must belong to this booking
        if booking.companion_id != companion.id:
            raise UnauthorizedTrackingAccessException()

        update = LocationUpdateRepository.create(booking, companion, data)

        # Keep CompanionProfile.current_latitude/longitude fresh
        try:
            profile = companion.companion_profile
            profile.current_latitude = data['latitude']
            profile.current_longitude = data['longitude']
            profile.location_updated_at = timezone.now()
            profile.save(update_fields=['current_latitude', 'current_longitude', 'location_updated_at'])
        except CompanionProfile.DoesNotExist:
            pass

        # Evaluate geofences
        GeofenceService.evaluate(booking, companion, lat, lon)

        # Broadcast to WebSocket group
        _broadcast(booking.id, constants.WS_TYPE_LOCATION_UPDATE, {
            'booking_id': str(booking.id),
            'latitude': lat,
            'longitude': lon,
            'speed': data.get('speed'),
            'heading': data.get('heading'),
            'recorded_at': update.recorded_at.isoformat(),
        })

        return update


class RouteService:

    @staticmethod
    def create_route(booking: Booking, data: dict) -> Route:
        route = RouteRepository.create(booking, data)
        logger.info("Route created for booking %s leg=%s", booking.id, data.get('leg'))
        return route

    @staticmethod
    def activate_route(booking: Booking, route_id) -> Route:
        route = RouteRepository.get_by_id(route_id)
        if not route or route.booking_id != booking.id:
            from .exceptions import RouteNotFoundException
            raise RouteNotFoundException()
        route = RouteRepository.activate(route)
        _broadcast(booking.id, constants.WS_TYPE_ROUTE_UPDATE, {
            'booking_id': str(booking.id),
            'route_id': str(route.id),
            'leg': route.leg,
            'status': route.status,
            'polyline': route.polyline,
            'estimated_arrival': route.estimated_arrival.isoformat() if route.estimated_arrival else None,
        })
        return route

    @staticmethod
    def complete_route(booking: Booking, route_id) -> Route:
        route = RouteRepository.get_by_id(route_id)
        if not route or route.booking_id != booking.id:
            from .exceptions import RouteNotFoundException
            raise RouteNotFoundException()
        route = RouteRepository.complete(route)
        _broadcast(booking.id, constants.WS_TYPE_ROUTE_UPDATE, {
            'booking_id': str(booking.id),
            'route_id': str(route.id),
            'leg': route.leg,
            'status': route.status,
        })
        return route

    @staticmethod
    def update_eta(booking: Booking, route_id, estimated_arrival) -> Route:
        route = RouteRepository.get_by_id(route_id)
        if not route or route.booking_id != booking.id:
            from .exceptions import RouteNotFoundException
            raise RouteNotFoundException()
        route = RouteRepository.update_eta(route, estimated_arrival)
        _broadcast(booking.id, constants.WS_TYPE_ETA_UPDATE, {
            'booking_id': str(booking.id),
            'route_id': str(route.id),
            'estimated_arrival': estimated_arrival.isoformat() if estimated_arrival else None,
        })
        return route


class GeofenceService:

    @staticmethod
    def create_geofences_for_booking(booking: Booking) -> list[Geofence]:
        """
        Auto-create pickup, hospital, and drop geofences from booking data.
        Called when a booking transitions to confirmed/in_progress.
        """
        fences = []

        if booking.pickup_latitude and booking.pickup_longitude:
            fences.append(GeofenceRepository.create(booking, {
                'fence_type': constants.GEOFENCE_PICKUP,
                'name': f'Pickup — {booking.pickup_address[:100]}',
                'latitude': booking.pickup_latitude,
                'longitude': booking.pickup_longitude,
                'radius_meters': constants.DEFAULT_GEOFENCE_RADIUS_METERS,
            }))

        if booking.hospital_latitude and booking.hospital_longitude:
            fences.append(GeofenceRepository.create(booking, {
                'fence_type': constants.GEOFENCE_HOSPITAL,
                'name': f'Hospital — {booking.hospital_name[:100]}',
                'latitude': booking.hospital_latitude,
                'longitude': booking.hospital_longitude,
                'radius_meters': constants.DEFAULT_GEOFENCE_RADIUS_METERS,
            }))

        logger.info("Created %d geofences for booking %s", len(fences), booking.id)
        return fences

    @staticmethod
    def evaluate(booking: Booking, companion, lat: float, lon: float):
        """
        Check every active geofence for this booking.
        If the companion has entered or exited a zone, log the event and broadcast.
        """
        active_fences = GeofenceRepository.get_active_for_booking(booking.id)
        for fence in active_fences:
            inside = is_inside_geofence(
                lat, lon,
                float(fence.latitude), float(fence.longitude),
                fence.radius_meters,
            )
            # Determine last known state from most recent event
            last_event = (
                GeofenceEvent.objects
                .filter(geofence=fence, booking=booking)
                .order_by('-occurred_at')
                .first()
            )
            last_type = last_event.event_type if last_event else None

            if inside and last_type != constants.GEOFENCE_EVENT_ENTER:
                event = GeofenceEventRepository.create(
                    fence, booking, companion,
                    constants.GEOFENCE_EVENT_ENTER, lat, lon,
                )
                _broadcast(booking.id, constants.WS_TYPE_GEOFENCE_EVENT, {
                    'booking_id': str(booking.id),
                    'geofence_id': str(fence.id),
                    'fence_type': fence.fence_type,
                    'event_type': constants.GEOFENCE_EVENT_ENTER,
                    'occurred_at': event.occurred_at.isoformat(),
                })
                logger.info("Companion %s ENTERED geofence %s for booking %s", companion.id, fence.id, booking.id)

            elif not inside and last_type == constants.GEOFENCE_EVENT_ENTER:
                event = GeofenceEventRepository.create(
                    fence, booking, companion,
                    constants.GEOFENCE_EVENT_EXIT, lat, lon,
                )
                _broadcast(booking.id, constants.WS_TYPE_GEOFENCE_EVENT, {
                    'booking_id': str(booking.id),
                    'geofence_id': str(fence.id),
                    'fence_type': fence.fence_type,
                    'event_type': constants.GEOFENCE_EVENT_EXIT,
                    'occurred_at': event.occurred_at.isoformat(),
                })
                logger.info("Companion %s EXITED geofence %s for booking %s", companion.id, fence.id, booking.id)
