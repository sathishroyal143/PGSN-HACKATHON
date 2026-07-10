"""AI Engine permissions."""
from rest_framework.permissions import BasePermission


class IsAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN'
        )
