"""Companions views."""
import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from common.responses import success_response, created_response
from common.exceptions import ResourceNotFoundException, PermissionDeniedException
from apps.users.models import UserRole
from .serializers import (
    CompanionProfileListSerializer, CompanionProfileDetailSerializer,
    CompanionProfileWriteSerializer, AvailabilityUpdateSerializer, LocationUpdateSerializer,
    CompanionSkillSerializer, CompanionAvailabilitySlotSerializer,
)
from .selectors import CompanionSelectors
from .services import CompanionService
from .permissions import IsCompanionOwnerOrAdmin
from .models import CompanionSkill, CompanionAvailabilitySlot

logger = logging.getLogger('carebridge')


class CompanionListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter('q', str, description='Search query')],
        responses=CompanionProfileListSerializer(many=True),
        tags=['Companions'],
    )
    def get(self, request):
        query = request.query_params.get('q')
        if query:
            companions = CompanionSelectors.search_companions(query)
        else:
            companions = CompanionSelectors.list_available()
        return success_response(CompanionProfileListSerializer(companions, many=True).data)


class CompanionProfileCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CompanionProfileWriteSerializer, responses=CompanionProfileDetailSerializer, tags=['Companions'])
    def post(self, request):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companion users can create a companion profile.")
        serializer = CompanionProfileWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = CompanionService.create_profile(request.user, serializer.validated_data)
        return created_response(CompanionProfileDetailSerializer(profile).data, 'Companion profile created.')


class CompanionProfileDetailView(APIView):
    permission_classes = [IsAuthenticated, IsCompanionOwnerOrAdmin]

    def _get_profile(self, pk):
        profile = CompanionSelectors.get_companion(pk)
        if not profile:
            raise ResourceNotFoundException("Companion profile not found.")
        self.check_object_permissions(self.request, profile)
        return profile

    @extend_schema(responses=CompanionProfileDetailSerializer, tags=['Companions'])
    def get(self, request, pk):
        return success_response(CompanionProfileDetailSerializer(self._get_profile(pk)).data)

    @extend_schema(request=CompanionProfileWriteSerializer, responses=CompanionProfileDetailSerializer, tags=['Companions'])
    def patch(self, request, pk):
        profile = self._get_profile(pk)
        serializer = CompanionProfileWriteSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = CompanionService.update_profile(pk, serializer.validated_data)
        return success_response(CompanionProfileDetailSerializer(updated).data, 'Profile updated.')


class MyCompanionProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CompanionProfileDetailSerializer, tags=['Companions'])
    def get(self, request):
        profile = CompanionSelectors.get_my_profile(request.user.id)
        if not profile:
            raise ResourceNotFoundException("Companion profile not found.")
        return success_response(CompanionProfileDetailSerializer(profile).data)


class CompanionAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AvailabilityUpdateSerializer, responses=CompanionProfileDetailSerializer, tags=['Companions'])
    def patch(self, request):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companions can update availability.")
        serializer = AvailabilityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = CompanionService.update_availability(
            request.user.id, serializer.validated_data['availability_status']
        )
        return success_response(CompanionProfileDetailSerializer(profile).data, 'Availability updated.')


class CompanionLocationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=LocationUpdateSerializer, tags=['Companions'])
    def post(self, request):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companions can update location.")
        serializer = LocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        CompanionService.update_location(
            request.user.id,
            serializer.validated_data['latitude'],
            serializer.validated_data['longitude'],
        )
        return success_response(message='Location updated.')


class CompanionSkillListView(APIView):
    """List and add skills for the authenticated companion."""
    permission_classes = [IsAuthenticated]

    def _get_profile(self):
        profile = CompanionSelectors.get_my_profile(self.request.user.id)
        if not profile:
            raise ResourceNotFoundException("Companion profile not found.")
        return profile

    @extend_schema(responses=CompanionSkillSerializer(many=True), tags=['Companions'])
    def get(self, request):
        profile = self._get_profile()
        return success_response(CompanionSkillSerializer(profile.skills.all(), many=True).data)

    @extend_schema(request=CompanionSkillSerializer, responses=CompanionSkillSerializer, tags=['Companions'])
    def post(self, request):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companions can manage skills.")
        profile = self._get_profile()
        serializer = CompanionSkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        skill, _ = CompanionSkill.objects.get_or_create(
            companion=profile,
            skill=serializer.validated_data['skill'],
            defaults={'proficiency_level': serializer.validated_data.get('proficiency_level', 1)},
        )
        return created_response(CompanionSkillSerializer(skill).data, 'Skill added.')


class CompanionSkillDetailView(APIView):
    """Update or delete a specific skill."""
    permission_classes = [IsAuthenticated]

    def _get_skill(self, skill_id):
        profile = CompanionSelectors.get_my_profile(self.request.user.id)
        if not profile:
            raise ResourceNotFoundException("Companion profile not found.")
        skill = CompanionSkill.objects.filter(id=skill_id, companion=profile).first()
        if not skill:
            raise ResourceNotFoundException("Skill not found.")
        return skill

    @extend_schema(request=CompanionSkillSerializer, responses=CompanionSkillSerializer, tags=['Companions'])
    def patch(self, request, skill_id):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companions can manage skills.")
        skill = self._get_skill(skill_id)
        serializer = CompanionSkillSerializer(skill, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(serializer.data, 'Skill updated.')

    @extend_schema(tags=['Companions'])
    def delete(self, request, skill_id):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companions can manage skills.")
        skill = self._get_skill(skill_id)
        skill.delete()
        return success_response(message='Skill removed.')


class CompanionSlotListView(APIView):
    """List and add availability slots for the authenticated companion."""
    permission_classes = [IsAuthenticated]

    def _get_profile(self):
        profile = CompanionSelectors.get_my_profile(self.request.user.id)
        if not profile:
            raise ResourceNotFoundException("Companion profile not found.")
        return profile

    @extend_schema(responses=CompanionAvailabilitySlotSerializer(many=True), tags=['Companions'])
    def get(self, request):
        profile = self._get_profile()
        return success_response(CompanionAvailabilitySlotSerializer(profile.availability_slots.all(), many=True).data)

    @extend_schema(request=CompanionAvailabilitySlotSerializer, responses=CompanionAvailabilitySlotSerializer, tags=['Companions'])
    def post(self, request):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companions can manage availability slots.")
        profile = self._get_profile()
        serializer = CompanionAvailabilitySlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot = CompanionAvailabilitySlot.objects.create(companion=profile, **serializer.validated_data)
        return created_response(CompanionAvailabilitySlotSerializer(slot).data, 'Slot added.')


class CompanionSlotDetailView(APIView):
    """Update or delete a specific availability slot."""
    permission_classes = [IsAuthenticated]

    def _get_slot(self, slot_id):
        profile = CompanionSelectors.get_my_profile(self.request.user.id)
        if not profile:
            raise ResourceNotFoundException("Companion profile not found.")
        slot = CompanionAvailabilitySlot.objects.filter(id=slot_id, companion=profile).first()
        if not slot:
            raise ResourceNotFoundException("Availability slot not found.")
        return slot

    @extend_schema(request=CompanionAvailabilitySlotSerializer, responses=CompanionAvailabilitySlotSerializer, tags=['Companions'])
    def patch(self, request, slot_id):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companions can manage availability slots.")
        slot = self._get_slot(slot_id)
        serializer = CompanionAvailabilitySlotSerializer(slot, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(serializer.data, 'Slot updated.')

    @extend_schema(tags=['Companions'])
    def delete(self, request, slot_id):
        if request.user.role != UserRole.COMPANION:
            raise PermissionDeniedException("Only companions can manage availability slots.")
        slot = self._get_slot(slot_id)
        slot.delete()
        return success_response(message='Slot removed.')
