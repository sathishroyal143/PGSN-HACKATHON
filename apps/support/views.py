"""Support views."""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import serializers as drf_serializers, status

from .selectors import FAQSelectors, TicketSelectors
from .services import ChatbotService, TicketService
from .repositories import TicketRepository
from .serializers import (
    ChatbotSerializer, CreateTicketSerializer, FAQSerializer,
    ReplyTicketSerializer, TicketMessageSerializer, TicketSerializer,
)
from . import constants


class TicketListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = TicketSelectors.for_user(request.user.id)
        return Response({'data': TicketSerializer(qs, many=True).data})

    def post(self, request):
        ser = CreateTicketSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        ticket = TicketService.create(
            user_id=request.user.id,
            subject=d['subject'],
            description=d['description'],
            category=d.get('category', 'other'),
            priority=d.get('priority', 'medium'),
        )
        return Response({'data': TicketSerializer(ticket).data}, status=status.HTTP_201_CREATED)


class TicketDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        ticket = TicketRepository.get_by_id(ticket_id)
        if not ticket:
            return Response({'error': 'Ticket not found.'}, status=status.HTTP_404_NOT_FOUND)
        messages = TicketSelectors.messages(ticket_id)
        return Response({
            'data': TicketSerializer(ticket).data,
            'messages': TicketMessageSerializer(messages, many=True).data,
        })

    def post(self, request, ticket_id):
        ser = ReplyTicketSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        msg = TicketService.reply(ticket_id, request.user.id, ser.validated_data['body'])
        return Response({'data': TicketMessageSerializer(msg).data}, status=status.HTTP_201_CREATED)


class FAQListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get('category')
        qs = FAQSelectors.published(category)
        return Response({'data': FAQSerializer(qs, many=True).data})


class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = ChatbotSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        response, intent = ChatbotService.respond(request.user.id, ser.validated_data['message'])
        return Response({'data': {'response': response, 'intent': intent}})


class AdminTicketListView(APIView):
    """Admin/Support: list all tickets with optional status filter."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        status_filter = request.query_params.get('status')
        qs = TicketRepository.get_all()
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response({'data': TicketSerializer(qs, many=True).data})


class AdminTicketDetailView(APIView):
    """Admin/Support: update ticket status, assign, resolve."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    class _UpdateSerializer(drf_serializers.Serializer):
        status = drf_serializers.ChoiceField(
            choices=[c[0] for c in constants.TICKET_STATUS_CHOICES], required=False
        )
        resolution_notes = drf_serializers.CharField(required=False, allow_blank=True)
        assigned_to = drf_serializers.UUIDField(required=False, allow_null=True)

    def patch(self, request, ticket_id):
        ticket = TicketRepository.get_by_id(ticket_id)
        if not ticket:
            return Response({'error': 'Ticket not found.'}, status=status.HTTP_404_NOT_FOUND)
        ser = self._UpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        if 'status' in d:
            TicketRepository.update_status(
                ticket_id, d['status'], d.get('resolution_notes', '')
            )
        if 'assigned_to' in d:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            assignee = User.objects.filter(id=d['assigned_to']).first() if d['assigned_to'] else None
            ticket.assigned_to = assignee
            ticket.save(update_fields=['assigned_to'])
        ticket.refresh_from_db()
        return Response({'data': TicketSerializer(ticket).data})

    def post(self, request, ticket_id):
        """Staff reply to a ticket."""
        ser = ReplyTicketSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        msg = TicketService.reply(ticket_id, request.user.id, ser.validated_data['body'], is_staff_reply=True)
        return Response({'data': TicketMessageSerializer(msg).data}, status=status.HTTP_201_CREATED)
