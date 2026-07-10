"""Dashboard views."""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.models import UserRole
from .selectors import DashboardSelectors


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, 'role', 'family')

        if role == UserRole.ADMIN:
            stats = DashboardSelectors.admin_stats()
            recent = []
        elif role == UserRole.COMPANION:
            stats = DashboardSelectors.companion_stats(user.id)
            recent = DashboardSelectors.recent_bookings(user.id, role='companion')
        else:
            stats = DashboardSelectors.family_stats(user.id)
            recent = DashboardSelectors.recent_bookings(user.id, role='family')

        return Response({'data': {'stats': stats, 'recent_bookings': recent, 'role': role}})
