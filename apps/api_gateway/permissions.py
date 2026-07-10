"""API Gateway permissions."""
from rest_framework.permissions import BasePermission


class IsGatewayAdmin(BasePermission):
    message = 'Administrator access is required for API Gateway management.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN'
        )
