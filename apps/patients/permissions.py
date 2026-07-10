"""Permissions for the Patients module."""
from rest_framework.permissions import BasePermission
from apps.users.models import UserRole


class IsFamilyUser(BasePermission):
    """Allow access only to users with FAMILY role."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.FAMILY
        )


class IsFamilyOrAdmin(BasePermission):
    """Allow access to FAMILY users or ADMIN users."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (UserRole.FAMILY, UserRole.ADMIN)
        )


class IsAdminUser(BasePermission):
    """Allow access only to ADMIN users."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )


class CanAccessPatient(BasePermission):
    """
    Object-level permission.
    Family users can only access patients belonging to their family profile.
    Admins can access all.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.ADMIN:
            return True
        try:
            return obj.family_profile == request.user.family_profile
        except Exception:
            return False
