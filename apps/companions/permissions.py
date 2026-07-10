"""Companions permissions."""
from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import UserRole


class IsCompanionOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.ADMIN or request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class IsCompanion(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.COMPANION
