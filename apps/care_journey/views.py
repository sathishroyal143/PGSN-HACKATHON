"""Care Journey views."""
import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.responses import success_response, created_response
from common.exceptions import ResourceNotFoundException, PermissionDeniedException
from apps.users.models import UserRole
from .serializers import (
    CareJourneyListSerializer, CareJourneyDetailSerializer,
    StartJourneySerializer, AdvanceStepSerializer, UpdateNotesSerializer,
)
from .selectors import CareJourneySelectors
from .services import CareJourneyService
from .permissions import IsJourneyParticipant, IsAdminUser

logger = logging.getLogger('carebridge')


class JourneyListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CareJourneyListSerializer(many=True), tags=['Care Journey'])
    def get(self, request):
        user = request.user
        if user.role == UserRole.ADMIN:
            journeys = CareJourneySelectors.get_active_journeys()
        else:
            from .models import CareJourney
            from apps.users.models import UserRole as UR
            if user.role == UR.COMPANION:
                journeys = CareJourney.objects.filter(
                    booking__companion=user
                ).select_related('booking').prefetch_related('steps')
            else:
                journeys = CareJourney.objects.filter(
                    booking__family_user=user
                ).select_related('booking').prefetch_related('steps')
        return success_response(CareJourneyListSerializer(journeys, many=True).data)

    @extend_schema(request=StartJourneySerializer, responses=CareJourneyDetailSerializer, tags=['Care Journey'])
    def post(self, request):
        serializer = StartJourneySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        journey = CareJourneyService.start_journey(
            serializer.validated_data['booking_id'], request.user
        )
        return created_response(CareJourneyDetailSerializer(journey).data, 'Journey started.')


class JourneyDetailView(APIView):
    permission_classes = [IsAuthenticated, IsJourneyParticipant]

    def _get_journey(self, pk):
        journey = CareJourneySelectors.get_journey(pk)
        if not journey:
            raise ResourceNotFoundException("Journey not found.")
        self.check_object_permissions(self.request, journey)
        return journey

    @extend_schema(responses=CareJourneyDetailSerializer, tags=['Care Journey'])
    def get(self, request, pk):
        return success_response(CareJourneyDetailSerializer(self._get_journey(pk)).data)


class JourneyByBookingView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CareJourneyDetailSerializer, tags=['Care Journey'])
    def get(self, request, booking_id):
        journey = CareJourneySelectors.get_by_booking(booking_id)
        if not journey:
            raise ResourceNotFoundException("Journey not found for this booking.")
        return success_response(CareJourneyDetailSerializer(journey).data)


class JourneyAdvanceStepView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AdvanceStepSerializer, responses=CareJourneyDetailSerializer, tags=['Care Journey'])
    def patch(self, request, pk):
        if request.user.role not in [UserRole.COMPANION, UserRole.ADMIN]:
            raise PermissionDeniedException("Only companions or admins can advance steps.")
        serializer = AdvanceStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        journey = CareJourneyService.advance_step(
            pk,
            serializer.validated_data['step_code'],
            serializer.validated_data['status'],
            request.user,
            serializer.validated_data.get('notes', ''),
        )
        return success_response(CareJourneyDetailSerializer(journey).data, 'Step updated.')


class JourneyNotesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=UpdateNotesSerializer, responses=CareJourneyDetailSerializer, tags=['Care Journey'])
    def patch(self, request, pk):
        if request.user.role not in [UserRole.COMPANION, UserRole.ADMIN]:
            raise PermissionDeniedException("Only companions or admins can update notes.")
        serializer = UpdateNotesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        journey = CareJourneyService.update_notes(
            pk, serializer.validated_data['companion_notes'], request.user
        )
        return success_response(CareJourneyDetailSerializer(journey).data, 'Notes updated.')


class JourneyCancelView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(responses=CareJourneyDetailSerializer, tags=['Care Journey'])
    def post(self, request, pk):
        journey = CareJourneyService.cancel_journey(pk, request.user)
        return success_response(CareJourneyDetailSerializer(journey).data, 'Journey cancelled.')
