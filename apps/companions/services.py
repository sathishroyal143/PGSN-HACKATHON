"""Companions business logic."""
import logging
from django.utils import timezone
from common.exceptions import ValidationException, ResourceNotFoundException, BusinessLogicException
from .models import CompanionProfile, CompanionSkill, CompanionAvailabilitySlot
from .repositories import CompanionRepository
from . import constants

logger = logging.getLogger('carebridge')


class CompanionService:
    @staticmethod
    def create_profile(user, data: dict) -> CompanionProfile:
        if CompanionProfile.objects.filter(user=user, is_deleted=False).exists():
            raise ValidationException("Companion profile already exists for this user.")
        skills_data = data.pop('skills', [])
        slots_data = data.pop('availability_slots', [])
        profile = CompanionProfile.objects.create(user=user, **data)
        for skill in skills_data:
            CompanionSkill.objects.create(companion=profile, **skill)
        for slot in slots_data:
            CompanionAvailabilitySlot.objects.create(companion=profile, **slot)
        logger.info(f"CompanionProfile created for user {user.id}")
        return profile

    @staticmethod
    def update_profile(pk, data: dict) -> CompanionProfile:
        profile = CompanionRepository.get_by_id(pk)
        if not profile:
            raise ResourceNotFoundException("Companion profile not found.")
        for field, value in data.items():
            setattr(profile, field, value)
        profile.save()
        return profile

    @staticmethod
    def update_availability(user_id, availability_status: str) -> CompanionProfile:
        profile = CompanionRepository.get_by_user(user_id)
        if not profile:
            raise ResourceNotFoundException("Companion profile not found.")
        if profile.status != constants.STATUS_ACTIVE:
            raise BusinessLogicException("Only active companions can update availability.")
        profile.availability_status = availability_status
        profile.save(update_fields=['availability_status', 'updated_at'])
        return profile

    @staticmethod
    def update_location(user_id, latitude, longitude) -> CompanionProfile:
        profile = CompanionRepository.get_by_user(user_id)
        if not profile:
            raise ResourceNotFoundException("Companion profile not found.")
        profile.current_latitude = latitude
        profile.current_longitude = longitude
        profile.location_updated_at = timezone.now()
        profile.save(update_fields=['current_latitude', 'current_longitude', 'location_updated_at'])
        return profile

    @staticmethod
    def update_rating(companion_id, new_rating: float):
        profile = CompanionRepository.get_by_id(companion_id)
        if not profile:
            return
        total = profile.total_reviews
        current_avg = float(profile.average_rating)
        new_avg = ((current_avg * total) + new_rating) / (total + 1)
        profile.average_rating = round(new_avg, 2)
        profile.total_reviews = total + 1
        profile.save(update_fields=['average_rating', 'total_reviews'])
