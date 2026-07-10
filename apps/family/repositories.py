"""
Repository layer for Family module.
All database queries are centralised here — views and services never query ORM directly.
"""
from django.db import transaction
from django.utils import timezone
from .models import FamilyProfile, FamilyMember, EmergencyContact


class FamilyProfileRepository:

    @staticmethod
    def get_by_user(user):
        try:
            return FamilyProfile.objects.get(user=user, is_deleted=False)
        except FamilyProfile.DoesNotExist:
            return None

    @staticmethod
    def get_by_id(profile_id):
        try:
            return FamilyProfile.objects.get(id=profile_id, is_deleted=False)
        except FamilyProfile.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create(user, **kwargs):
        return FamilyProfile.objects.create(user=user, **kwargs)

    @staticmethod
    @transaction.atomic
    def update(profile, **kwargs):
        for field, value in kwargs.items():
            setattr(profile, field, value)
        profile.save()
        return profile

    @staticmethod
    @transaction.atomic
    def soft_delete(profile):
        profile.is_deleted = True
        profile.deleted_at = timezone.now()
        profile.save(update_fields=['is_deleted', 'deleted_at'])


class FamilyMemberRepository:

    @staticmethod
    def get_by_id(member_id):
        try:
            return FamilyMember.objects.get(id=member_id, is_deleted=False)
        except FamilyMember.DoesNotExist:
            return None

    @staticmethod
    def get_by_profile(profile):
        return FamilyMember.objects.filter(
            family_profile=profile, is_deleted=False
        ).order_by('-is_primary_patient', 'first_name')

    @staticmethod
    def get_primary(profile):
        return FamilyMember.objects.filter(
            family_profile=profile, is_primary_patient=True, is_deleted=False
        ).first()

    @staticmethod
    @transaction.atomic
    def create(profile, **kwargs):
        # Only one primary patient allowed per profile
        if kwargs.get('is_primary_patient'):
            FamilyMember.objects.filter(
                family_profile=profile, is_primary_patient=True
            ).update(is_primary_patient=False)
        return FamilyMember.objects.create(family_profile=profile, **kwargs)

    @staticmethod
    @transaction.atomic
    def update(member, **kwargs):
        if kwargs.get('is_primary_patient'):
            FamilyMember.objects.filter(
                family_profile=member.family_profile, is_primary_patient=True
            ).exclude(id=member.id).update(is_primary_patient=False)
        for field, value in kwargs.items():
            setattr(member, field, value)
        member.save()
        return member

    @staticmethod
    @transaction.atomic
    def soft_delete(member):
        member.is_deleted = True
        member.deleted_at = timezone.now()
        member.save(update_fields=['is_deleted', 'deleted_at'])

    @staticmethod
    def count_active(profile):
        return FamilyMember.objects.filter(
            family_profile=profile, is_deleted=False, is_active=True
        ).count()


class EmergencyContactRepository:

    @staticmethod
    def get_by_id(contact_id):
        try:
            return EmergencyContact.objects.get(id=contact_id)
        except EmergencyContact.DoesNotExist:
            return None

    @staticmethod
    def get_by_profile(profile):
        return EmergencyContact.objects.filter(
            family_profile=profile
        ).order_by('-is_primary', 'name')

    @staticmethod
    def get_primary(profile):
        return EmergencyContact.objects.filter(
            family_profile=profile, is_primary=True
        ).first()

    @staticmethod
    @transaction.atomic
    def create(profile, **kwargs):
        if kwargs.get('is_primary'):
            EmergencyContact.objects.filter(
                family_profile=profile, is_primary=True
            ).update(is_primary=False)
        return EmergencyContact.objects.create(family_profile=profile, **kwargs)

    @staticmethod
    @transaction.atomic
    def update(contact, **kwargs):
        if kwargs.get('is_primary'):
            EmergencyContact.objects.filter(
                family_profile=contact.family_profile, is_primary=True
            ).exclude(id=contact.id).update(is_primary=False)
        for field, value in kwargs.items():
            setattr(contact, field, value)
        contact.save()
        return contact

    @staticmethod
    def delete(contact):
        contact.delete()

    @staticmethod
    def count(profile):
        return EmergencyContact.objects.filter(family_profile=profile).count()
