"""
Selectors for Family module — read-only query helpers used by views.
"""
from .repositories import (
    FamilyProfileRepository,
    FamilyMemberRepository,
    EmergencyContactRepository,
)


class FamilySelector:

    @staticmethod
    def get_profile_summary(user):
        """Return a lightweight dict summary of the family profile."""
        profile = FamilyProfileRepository.get_by_user(user)
        if not profile:
            return None

        members  = FamilyMemberRepository.get_by_profile(profile)
        contacts = EmergencyContactRepository.get_by_profile(profile)
        primary  = FamilyMemberRepository.get_primary(profile)

        return {
            'profile_id':              str(profile.id),
            'preferred_language':      profile.preferred_language,
            'preferred_contact_method':profile.preferred_contact_method,
            'is_premium':              profile.is_premium,
            'total_members':           members.count(),
            'total_emergency_contacts':contacts.count(),
            'primary_patient':         primary.get_full_name() if primary else None,
        }
