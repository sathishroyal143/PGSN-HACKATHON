"""
Service layer for Family module.
All business logic lives here. Views stay thin.
"""
from django.db import transaction
from django.utils import timezone
from common.exceptions import (
    ResourceNotFoundException,
    PermissionDeniedException,
    BusinessLogicException,
    ConflictException,
)
from .repositories import (
    FamilyProfileRepository,
    FamilyMemberRepository,
    EmergencyContactRepository,
)
import logging

logger = logging.getLogger(__name__)

MAX_FAMILY_MEMBERS    = 10
MAX_EMERGENCY_CONTACTS = 5


class FamilyProfileService:

    @staticmethod
    @transaction.atomic
    def get_or_create_profile(user):
        """
        Return existing FamilyProfile or create one for the user.
        Called after registration to ensure every FAMILY user has a profile.
        """
        profile = FamilyProfileRepository.get_by_user(user)
        if not profile:
            profile = FamilyProfileRepository.create(user=user)
            logger.info(f"FamilyProfile created for user {user.email}")
        return profile

    @staticmethod
    def get_profile(user):
        profile = FamilyProfileRepository.get_by_user(user)
        if not profile:
            raise ResourceNotFoundException('Family profile not found.')
        return profile

    @staticmethod
    @transaction.atomic
    def update_profile(user, validated_data):
        profile = FamilyProfileService.get_profile(user)
        updated = FamilyProfileRepository.update(profile, **validated_data)
        logger.info(f"FamilyProfile updated for user {user.email}")
        return updated


class FamilyMemberService:

    @staticmethod
    def list_members(user):
        profile = FamilyProfileService.get_profile(user)
        return FamilyMemberRepository.get_by_profile(profile)

    @staticmethod
    @transaction.atomic
    def add_member(user, validated_data):
        profile = FamilyProfileService.get_profile(user)

        active_count = FamilyMemberRepository.count_active(profile)
        if active_count >= MAX_FAMILY_MEMBERS:
            raise BusinessLogicException(
                f'Maximum {MAX_FAMILY_MEMBERS} family members allowed per account.'
            )

        member = FamilyMemberRepository.create(profile, **validated_data)
        logger.info(f"FamilyMember '{member.get_full_name()}' added for user {user.email}")
        return member

    @staticmethod
    def get_member(user, member_id):
        profile = FamilyProfileService.get_profile(user)
        member  = FamilyMemberRepository.get_by_id(member_id)
        if not member or member.family_profile_id != profile.id:
            raise ResourceNotFoundException('Family member not found.')
        return member

    @staticmethod
    @transaction.atomic
    def update_member(user, member_id, validated_data):
        member = FamilyMemberService.get_member(user, member_id)
        updated = FamilyMemberRepository.update(member, **validated_data)
        logger.info(f"FamilyMember {member_id} updated for user {user.email}")
        return updated

    @staticmethod
    @transaction.atomic
    def delete_member(user, member_id):
        member = FamilyMemberService.get_member(user, member_id)
        FamilyMemberRepository.soft_delete(member)
        logger.info(f"FamilyMember {member_id} deleted for user {user.email}")


class EmergencyContactService:

    @staticmethod
    def list_contacts(user):
        profile = FamilyProfileService.get_profile(user)
        return EmergencyContactRepository.get_by_profile(profile)

    @staticmethod
    @transaction.atomic
    def add_contact(user, validated_data):
        profile = FamilyProfileService.get_profile(user)

        count = EmergencyContactRepository.count(profile)
        if count >= MAX_EMERGENCY_CONTACTS:
            raise BusinessLogicException(
                f'Maximum {MAX_EMERGENCY_CONTACTS} emergency contacts allowed.'
            )

        contact = EmergencyContactRepository.create(profile, **validated_data)
        logger.info(f"EmergencyContact '{contact.name}' added for user {user.email}")
        return contact

    @staticmethod
    def get_contact(user, contact_id):
        profile = FamilyProfileService.get_profile(user)
        contact = EmergencyContactRepository.get_by_id(contact_id)
        if not contact or contact.family_profile_id != profile.id:
            raise ResourceNotFoundException('Emergency contact not found.')
        return contact

    @staticmethod
    @transaction.atomic
    def update_contact(user, contact_id, validated_data):
        contact = EmergencyContactService.get_contact(user, contact_id)
        updated = EmergencyContactRepository.update(contact, **validated_data)
        logger.info(f"EmergencyContact {contact_id} updated for user {user.email}")
        return updated

    @staticmethod
    @transaction.atomic
    def delete_contact(user, contact_id):
        contact = EmergencyContactService.get_contact(user, contact_id)
        EmergencyContactRepository.delete(contact)
        logger.info(f"EmergencyContact {contact_id} deleted for user {user.email}")
