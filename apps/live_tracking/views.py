"""Live Tracking views — thin REST layer."""
import logging

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.bookings.models import Booking
from common.exceptions import ResourceNotFoundException
from common.responses import (
    created_response,
    deleted_response,
    success_response,
)

from .permissions import IsBookingParticipant, IsCompanionOfBooking
from .selectors import TrackingSelectors
from .serializers import (
    GeofenceCreateSerializer,
    GeofenceEventSerializer,
    GeofenceSerializer,
    LocationUpdateCreateSerializer,
    LocationUpdateSerializer,
    RouteCreateSerializer,
    RouteETAUpdateSerializer,
    RouteSerializer,
    TrackingSummarySerializer,
)
from .services import GeofenceService, LocationService, RouteService

logger = logging.getLogger('carebridge')


def _get_booking_or_404(booking_id) -> Booking:
    booking = Booking.objects.filter(id=booking_id, is_deleted=False).first()
    if not booking:
        raise ResourceNotFoundException('Booking not found.')
    return booking


# ---------------------------------------------------------------------------
# Location Updates
# ---------------------------------------------------------------------------

@extend_schema(tags=['Live Tracking'])
class LocationUpdateView(APIView):
    """POST a GPS ping (companion only). GET the latest location (participants)."""

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCompanionOfBooking()]
        return [IsAuthenticated(), IsBookingParticipant()]

    @extend_schema(
        request=LocationUpdateCreateSerializer,
        responses={201: LocationUpdateSerializer},
        summary='Post GPS location update',
    )
    def post(self, request, booking_id):
        booking = _get_booking_or_404(booking_id)
        serializer = LocationUpdateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update = LocationService.record_location(booking, request.user, serializer.validated_data)
        return created_response(
            LocationUpdateSerializer(update).data,
            message='Location recorded.',
        )

    @extend_schema(
        responses={200: dict},
        summary='Get latest live location for a booking',
    )
    def get(self, request, booking_id):
        _get_booking_or_404(booking_id)
        data = TrackingSelectors.get_live_location(booking_id)
        return success_response(data, message='Live location retrieved.')


@extend_schema(tags=['Live Tracking'])
class LocationHistoryView(APIView):
    """GET the full GPS trail for a booking (participants only)."""
    permission_classes = [IsAuthenticated, IsBookingParticipant]

    @extend_schema(
        responses={200: list},
        summary='Get location history for a booking',
    )
    def get(self, request, booking_id):
        _get_booking_or_404(booking_id)
        limit = min(int(request.query_params.get('limit', 500)), 1000)
        data = TrackingSelectors.get_location_history(booking_id, limit)
        return success_response(data, message='Location history retrieved.')


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@extend_schema(tags=['Live Tracking'])
class RouteListCreateView(APIView):
    """List all routes or create a new route for a booking."""

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCompanionOfBooking()]
        return [IsAuthenticated(), IsBookingParticipant()]

    @extend_schema(responses={200: RouteSerializer(many=True)}, summary='List routes for a booking')
    def get(self, request, booking_id):
        _get_booking_or_404(booking_id)
        routes = TrackingSelectors.get_all_routes(booking_id)
        return success_response(RouteSerializer(routes, many=True).data)

    @extend_schema(request=RouteCreateSerializer, responses={201: RouteSerializer}, summary='Create a route')
    def post(self, request, booking_id):
        booking = _get_booking_or_404(booking_id)
        serializer = RouteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        route = RouteService.create_route(booking, serializer.validated_data)
        return created_response(RouteSerializer(route).data, message='Route created.')


@extend_schema(tags=['Live Tracking'])
class RouteActivateView(APIView):
    """Activate a planned route (companion only)."""
    permission_classes = [IsAuthenticated, IsCompanionOfBooking]

    @extend_schema(responses={200: RouteSerializer}, summary='Activate a route')
    def post(self, request, booking_id, route_id):
        booking = _get_booking_or_404(booking_id)
        route = RouteService.activate_route(booking, route_id)
        return success_response(RouteSerializer(route).data, message='Route activated.')


@extend_schema(tags=['Live Tracking'])
class RouteCompleteView(APIView):
    """Mark a route as completed (companion only)."""
    permission_classes = [IsAuthenticated, IsCompanionOfBooking]

    @extend_schema(responses={200: RouteSerializer}, summary='Complete a route')
    def post(self, request, booking_id, route_id):
        booking = _get_booking_or_404(booking_id)
        route = RouteService.complete_route(booking, route_id)
        return success_response(RouteSerializer(route).data, message='Route completed.')


@extend_schema(tags=['Live Tracking'])
class RouteETAView(APIView):
    """Update ETA for an active route (companion only)."""
    permission_classes = [IsAuthenticated, IsCompanionOfBooking]

    @extend_schema(
        request=RouteETAUpdateSerializer,
        responses={200: RouteSerializer},
        summary='Update route ETA',
    )
    def patch(self, request, booking_id, route_id):
        booking = _get_booking_or_404(booking_id)
        serializer = RouteETAUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        route = RouteService.update_eta(booking, route_id, serializer.validated_data['estimated_arrival'])
        return success_response(RouteSerializer(route).data, message='ETA updated.')


# ---------------------------------------------------------------------------
# Geofences
# ---------------------------------------------------------------------------

@extend_schema(tags=['Live Tracking'])
class GeofenceListCreateView(APIView):
    """List active geofences or create a custom geofence for a booking."""

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCompanionOfBooking()]
        return [IsAuthenticated(), IsBookingParticipant()]

    @extend_schema(responses={200: GeofenceSerializer(many=True)}, summary='List geofences')
    def get(self, request, booking_id):
        _get_booking_or_404(booking_id)
        fences = TrackingSelectors.get_active_geofences(booking_id)
        return success_response(GeofenceSerializer(fences, many=True).data)

    @extend_schema(request=GeofenceCreateSerializer, responses={201: GeofenceSerializer}, summary='Create geofence')
    def post(self, request, booking_id):
        booking = _get_booking_or_404(booking_id)
        serializer = GeofenceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from .repositories import GeofenceRepository
        fence = GeofenceRepository.create(booking, serializer.validated_data)
        return created_response(GeofenceSerializer(fence).data, message='Geofence created.')


@extend_schema(tags=['Live Tracking'])
class GeofenceEventListView(APIView):
    """List all geofence events for a booking (participants only)."""
    permission_classes = [IsAuthenticated, IsBookingParticipant]

    @extend_schema(responses={200: GeofenceEventSerializer(many=True)}, summary='List geofence events')
    def get(self, request, booking_id):
        _get_booking_or_404(booking_id)
        events = TrackingSelectors.get_geofence_events(booking_id)
        return success_response(GeofenceEventSerializer(events, many=True).data)


# ---------------------------------------------------------------------------
# Tracking Summary
# ---------------------------------------------------------------------------

@extend_schema(tags=['Live Tracking'])
class TrackingSummaryView(APIView):
    """Single endpoint returning live location + active route + geofences."""
    permission_classes = [IsAuthenticated, IsBookingParticipant]

    @extend_schema(
        responses={200: TrackingSummarySerializer},
        summary='Get full tracking summary for a booking',
    )
    def get(self, request, booking_id):
        _get_booking_or_404(booking_id)
        data = TrackingSelectors.get_tracking_summary(booking_id)
        return success_response(data, message='Tracking summary retrieved.')
