"""Care Journey permissions."""
from rest_framework.permissions import BasePermission
from apps.users.models import UserRole


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN


class IsJourneyParticipant(BasePermission):
    """Allow access to the family user, assigned companion, or admin."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == UserRole.ADMIN:
            return True
        booking = obj.booking
        if user.role == UserRole.FAMILY and booking.family_user_id == user.id:
            return True
        if user.role == UserRole.COMPANION and booking.companion_id == user.id:
            return True
        return False
