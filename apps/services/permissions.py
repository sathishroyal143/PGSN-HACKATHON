"""
Care Services permissions.
Role-based access control for the services module.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import UserRole


class IsAdminOrReadOnly(BasePermission):
    """
    Allow read access to all authenticated users.
    Write access (POST/PUT/PATCH/DELETE) restricted to ADMIN role only.
    """

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == UserRole.ADMIN


class IsAdminUser(BasePermission):
    """Full access restricted to ADMIN role only."""

    def has_permission(self, request, view) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )


class IsCompanionUser(BasePermission):
    """Access restricted to COMPANION role."""

    def has_permission(self, request, view) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.COMPANION
        )
