"""
Views for Family module.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from common.responses import success_response, error_response, created_response, updated_response, deleted_response
from common.exceptions import CareBridgeBaseException
from .permissions import IsFamilyUser, IsFamilyOrAdmin
from .services import FamilyProfileService, FamilyMemberService, EmergencyContactService
from .selectors import FamilySelector
from .serializers import (
    FamilyProfileSerializer, FamilyProfileUpdateSerializer,
    FamilyMemberSerializer, FamilyMemberCreateSerializer, FamilyMemberUpdateSerializer,
    EmergencyContactSerializer, EmergencyContactCreateSerializer,
)
import logging

logger = logging.getLogger(__name__)


class FamilyProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [IsFamilyOrAdmin]

    @action(detail=False, methods=['get'], url_path='get')
    def get_profile(self, request):
        try:
            profile = FamilyProfileService.get_or_create_profile(request.user)
            return success_response(
                data=FamilyProfileSerializer(profile).data,
                message='Family profile retrieved successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Get family profile failed: {e}')
            return error_response(message='Failed to retrieve family profile.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['put', 'patch'], url_path='update')
    def update_profile(self, request):
        try:
            serializer = FamilyProfileUpdateSerializer(data=request.data, partial=request.method == 'PATCH')
            serializer.is_valid(raise_exception=True)
            profile = FamilyProfileService.update_profile(request.user, serializer.validated_data)
            return updated_response(
                data=FamilyProfileSerializer(profile).data,
                message='Family profile updated successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Update family profile failed: {e}')
            return error_response(message='Failed to update family profile.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        try:
            data = FamilySelector.get_profile_summary(request.user)
            return success_response(data=data, message='Summary retrieved successfully.')
        except Exception as e:
            logger.error(f'Get family summary failed: {e}')
            return error_response(message='Failed to retrieve summary.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FamilyMemberViewSet(viewsets.GenericViewSet):
    permission_classes = [IsFamilyUser]

    def list(self, request):
        try:
            members = FamilyMemberService.list_members(request.user)
            return success_response(
                data=FamilyMemberSerializer(members, many=True).data,
                message='Family members retrieved successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'List family members failed: {e}')
            return error_response(message='Failed to retrieve family members.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        try:
            serializer = FamilyMemberCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            member = FamilyMemberService.add_member(request.user, serializer.validated_data)
            return created_response(
                data=FamilyMemberSerializer(member).data,
                message='Family member added successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Add family member failed: {e}')
            return error_response(message='Failed to add family member.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        try:
            member = FamilyMemberService.get_member(request.user, pk)
            return success_response(
                data=FamilyMemberSerializer(member).data,
                message='Family member retrieved successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Get family member failed: {e}')
            return error_response(message='Failed to retrieve family member.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        try:
            serializer = FamilyMemberUpdateSerializer(data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            member = FamilyMemberService.update_member(request.user, pk, serializer.validated_data)
            return updated_response(
                data=FamilyMemberSerializer(member).data,
                message='Family member updated successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Update family member failed: {e}')
            return error_response(message='Failed to update family member.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk=None):
        try:
            serializer = FamilyMemberUpdateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            member = FamilyMemberService.update_member(request.user, pk, serializer.validated_data)
            return updated_response(
                data=FamilyMemberSerializer(member).data,
                message='Family member updated successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Partial update family member failed: {e}')
            return error_response(message='Failed to update family member.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        try:
            FamilyMemberService.delete_member(request.user, pk)
            return deleted_response(message='Family member deleted successfully.')
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Delete family member failed: {e}')
            return error_response(message='Failed to delete family member.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmergencyContactViewSet(viewsets.GenericViewSet):
    permission_classes = [IsFamilyUser]

    def list(self, request):
        try:
            contacts = EmergencyContactService.list_contacts(request.user)
            return success_response(
                data=EmergencyContactSerializer(contacts, many=True).data,
                message='Emergency contacts retrieved successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'List emergency contacts failed: {e}')
            return error_response(message='Failed to retrieve emergency contacts.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        try:
            serializer = EmergencyContactCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            contact = EmergencyContactService.add_contact(request.user, serializer.validated_data)
            return created_response(
                data=EmergencyContactSerializer(contact).data,
                message='Emergency contact added successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Add emergency contact failed: {e}')
            return error_response(message='Failed to add emergency contact.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        try:
            contact = EmergencyContactService.get_contact(request.user, pk)
            return success_response(
                data=EmergencyContactSerializer(contact).data,
                message='Emergency contact retrieved successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Get emergency contact failed: {e}')
            return error_response(message='Failed to retrieve emergency contact.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        try:
            serializer = EmergencyContactCreateSerializer(data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            contact = EmergencyContactService.update_contact(request.user, pk, serializer.validated_data)
            return updated_response(
                data=EmergencyContactSerializer(contact).data,
                message='Emergency contact updated successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Update emergency contact failed: {e}')
            return error_response(message='Failed to update emergency contact.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk=None):
        try:
            serializer = EmergencyContactCreateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            contact = EmergencyContactService.update_contact(request.user, pk, serializer.validated_data)
            return updated_response(
                data=EmergencyContactSerializer(contact).data,
                message='Emergency contact updated successfully.'
            )
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Partial update emergency contact failed: {e}')
            return error_response(message='Failed to update emergency contact.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        try:
            EmergencyContactService.delete_contact(request.user, pk)
            return deleted_response(message='Emergency contact deleted successfully.')
        except CareBridgeBaseException as e:
            return error_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            logger.error(f'Delete emergency contact failed: {e}')
            return error_response(message='Failed to delete emergency contact.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
