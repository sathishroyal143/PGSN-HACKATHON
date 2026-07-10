"""Companions repositories."""
from django.db.models import Q
from .models import CompanionProfile, CompanionSkill, CompanionAvailabilitySlot
from . import constants


class CompanionRepository:
    @staticmethod
    def get_by_id(pk):
        return CompanionProfile.objects.select_related('user').filter(pk=pk, is_deleted=False).first()

    @staticmethod
    def get_by_user(user_id):
        return CompanionProfile.objects.select_related('user').filter(user_id=user_id, is_deleted=False).first()

    @staticmethod
    def get_active_available():
        return CompanionProfile.objects.select_related('user').filter(
            status=constants.STATUS_ACTIVE,
            availability_status=constants.AVAILABILITY_AVAILABLE,
            is_deleted=False,
        ).prefetch_related('skills')

    @staticmethod
    def get_by_skill(skill_code):
        companion_ids = CompanionSkill.objects.filter(skill=skill_code, verified=True).values_list('companion_id', flat=True)
        return CompanionProfile.objects.filter(
            id__in=companion_ids,
            status=constants.STATUS_ACTIVE,
            is_deleted=False,
        ).select_related('user')

    @staticmethod
    def search(query):
        return CompanionProfile.objects.select_related('user').filter(
            Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query),
            status=constants.STATUS_ACTIVE,
            is_deleted=False,
        )
