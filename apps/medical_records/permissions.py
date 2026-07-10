"""Permissions for Medical Records module."""
from rest_framework.permissions import BasePermission
from apps.users.models import UserRole


class IsFamilyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (UserRole.FAMILY, UserRole.ADMIN)
        )


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )


class CanAccessMedicalRecord(BasePermission):
    """
    Object-level: family users can only access records for their own patients.
    Admins and companions (read-only during journey) can access all.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.ADMIN:
            return True
        if request.user.role == UserRole.COMPANION:
            return request.method in ('GET', 'HEAD', 'OPTIONS')
        try:
            return obj.patient.family_profile == request.user.family_profile
        except Exception:
            return False
