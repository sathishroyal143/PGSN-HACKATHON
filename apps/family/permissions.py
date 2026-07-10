"""
Permissions for Family module.
"""
from rest_framework.permissions import BasePermission
from apps.users.models import UserRole


class IsFamilyUser(BasePermission):
    """Allow access only to users with role=FAMILY."""
    message = 'Only Family users can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and not request.user.is_blocked
            and request.user.role == UserRole.FAMILY
        )


class IsFamilyOrAdmin(BasePermission):
    """Allow access to FAMILY users and ADMIN users."""
    message = 'Only Family or Admin users can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and not request.user.is_blocked
            and request.user.role in (UserRole.FAMILY, UserRole.ADMIN)
        )
