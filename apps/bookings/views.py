"""Bookings views."""
import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from common.responses import success_response, created_response
from common.exceptions import ResourceNotFoundException, PermissionDeniedException
from apps.users.models import UserRole
from .serializers import (
    BookingCreateSerializer, BookingListSerializer, BookingDetailSerializer,
    BookingStatusTransitionSerializer, BookingCancelSerializer, AssignCompanionSerializer,
    BookingRejectSerializer,
)
from .selectors import BookingSelectors
from .services import BookingService
from .permissions import IsBookingParticipant, IsAdminUser
from . import constants

logger = logging.getLogger('carebridge')


class BookingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter('status', str, description='Filter by status')],
        responses=BookingListSerializer(many=True),
        tags=['Bookings'],
    )
    def get(self, request):
        from .models import Booking
        status_filter = request.query_params.get('status')
        user = request.user
        if user.role == UserRole.FAMILY:
            bookings = BookingSelectors.family_bookings(user.id, status_filter)
        elif user.role == UserRole.COMPANION:
            bookings = BookingSelectors.companion_bookings(user.id, status_filter)
        else:
            from .models import Booking
            bookings = Booking.objects.select_related('patient', 'companion', 'service_package', 'care_service').order_by('-created_at')
            if status_filter:
                bookings = bookings.filter(status=status_filter)
        return success_response(BookingListSerializer(bookings, many=True).data)

    @extend_schema(request=BookingCreateSerializer, responses=BookingDetailSerializer, tags=['Bookings'])
    def post(self, request):
        if request.user.role != UserRole.FAMILY:
            raise PermissionDeniedException("Only family users can create bookings.")
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = BookingService.create_booking(serializer.validated_data, request.user)
        return created_response(BookingDetailSerializer(booking).data, 'Booking created.')


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated, IsBookingParticipant]

    def _get_booking(self, pk):
        booking = BookingSelectors.get_booking(pk)
        if not booking:
            raise ResourceNotFoundException("Booking not found.")
        self.check_object_permissions(self.request, booking)
        return booking

    @extend_schema(responses=BookingDetailSerializer, tags=['Bookings'])
    def get(self, request, pk):
        return success_response(BookingDetailSerializer(self._get_booking(pk)).data)


class BookingStatusView(APIView):
    permission_classes = [IsAuthenticated, IsBookingParticipant]

    @extend_schema(request=BookingStatusTransitionSerializer, responses=BookingDetailSerializer, tags=['Bookings'])
    def patch(self, request, pk):
        serializer = BookingStatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = BookingSelectors.get_booking(pk)
        if not booking:
            raise ResourceNotFoundException("Booking not found.")
        self.check_object_permissions(request, booking)
        booking = BookingService.transition_status(
            pk,
            serializer.validated_data['status'],
            request.user,
            serializer.validated_data.get('notes', ''),
        )
        return success_response(BookingDetailSerializer(booking).data, 'Status updated.')


class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated, IsBookingParticipant]

    @extend_schema(request=BookingCancelSerializer, responses=BookingDetailSerializer, tags=['Bookings'])
    def post(self, request, pk):
        booking = BookingSelectors.get_booking(pk)
        if not booking:
            raise ResourceNotFoundException("Booking not found.")
        self.check_object_permissions(request, booking)

        serializer = BookingCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cancel_by_map = {
            UserRole.FAMILY: 'FAMILY',
            UserRole.COMPANION: 'COMPANION',
            UserRole.ADMIN: 'ADMIN',
        }
        cancel_by = cancel_by_map.get(request.user.role, 'SYSTEM')
        booking = BookingService.cancel_booking(
            pk, request.user, serializer.validated_data['reason'], cancel_by
        )
        return success_response(BookingDetailSerializer(booking).data, 'Booking cancelled.')


class AssignCompanionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(request=AssignCompanionSerializer, responses=BookingDetailSerializer, tags=['Bookings'])
    def post(self, request, pk):
        serializer = AssignCompanionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        companion = User.objects.filter(
            id=serializer.validated_data['companion_id'],
            role=UserRole.COMPANION,
        ).first()
        if not companion:
            raise ResourceNotFoundException("Companion not found.")
        booking = BookingService.assign_companion(pk, companion, request.user)
        return success_response(BookingDetailSerializer(booking).data, 'Companion assigned.')


class CompanionAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=BookingDetailSerializer, tags=['Bookings'])
    def post(self, request, pk):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companion users can accept bookings.")
        booking = BookingService.accept_booking(pk, request.user)
        return success_response(BookingDetailSerializer(booking).data, 'Booking accepted successfully.')


class CompanionRejectView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=BookingRejectSerializer, responses=BookingDetailSerializer, tags=['Bookings'])
    def post(self, request, pk):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companion users can reject bookings.")
        serializer = BookingRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = BookingService.reject_booking(
            pk, request.user, serializer.validated_data.get('reason', '')
        )
        return success_response(BookingDetailSerializer(booking).data, 'Booking rejected successfully.')


class CompanionPendingRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=BookingListSerializer(many=True), tags=['Bookings'])
    def get(self, request):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companion users can view pending requests.")
        from .models import Booking
        # Retrieve bookings that are PENDING or CONFIRMED and do not have an assigned companion
        bookings = Booking.objects.filter(
            status__in=[constants.STATUS_PENDING, constants.STATUS_CONFIRMED],
            companion__isnull=True,
        ).exclude(
            status_logs__changed_by=request.user,
            status_logs__notes__icontains='rejected request'
        ).select_related('patient', 'companion', 'care_service').order_by('-created_at')
        return success_response(BookingListSerializer(bookings, many=True).data)

