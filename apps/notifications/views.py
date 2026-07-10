"""Notifications views."""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .selectors import NotificationSelectors
from .services import NotificationService
from .serializers import NotificationSerializer, NotificationPreferenceSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread_only = request.query_params.get('unread') == 'true'
        qs = NotificationSelectors.list_for_user(request.user.id, unread_only=unread_only)
        data = NotificationSerializer(qs, many=True).data
        return Response({
            'data': data,
            'unread_count': NotificationSelectors.unread_count(request.user.id),
        })


class MarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        NotificationService.mark_read(notification_id, request.user.id)
        return Response({'message': 'Marked as read.'})


class MarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = NotificationService.mark_all_read(request.user.id)
        return Response({'message': f'{count} notifications marked as read.'})


class NotificationDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, notification_id):
        NotificationService.delete(notification_id, request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pref = NotificationSelectors.get_preferences(request.user.id)
        return Response({'data': NotificationPreferenceSerializer(pref).data})

    def patch(self, request):
        allowed = {'in_app_enabled', 'email_enabled', 'sms_enabled', 'push_enabled', 'muted_types'}
        fields = {k: v for k, v in request.data.items() if k in allowed}
        pref = NotificationService.update_preferences(request.user.id, **fields)
        return Response({'data': NotificationPreferenceSerializer(pref).data})
