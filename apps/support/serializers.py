"""Support serializers."""
from rest_framework import serializers
from .models import ChatbotLog, FAQ, Ticket, TicketMessage
from . import constants


class TicketMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ['id', 'sender', 'body', 'is_staff_reply', 'created_at']
        read_only_fields = fields


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'user', 'subject', 'description', 'category', 'priority',
            'status', 'resolution_notes', 'resolved_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class CreateTicketSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    description = serializers.CharField()
    category = serializers.ChoiceField(
        choices=[c[0] for c in constants.TICKET_CATEGORY_CHOICES],
        default=constants.TICKET_CATEGORY_OTHER,
    )
    priority = serializers.ChoiceField(
        choices=[c[0] for c in constants.TICKET_PRIORITY_CHOICES],
        default=constants.TICKET_PRIORITY_MEDIUM,
    )


class ReplyTicketSerializer(serializers.Serializer):
    body = serializers.CharField()


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'category', 'question', 'answer', 'order']
        read_only_fields = fields


class ChatbotSerializer(serializers.Serializer):
    message = serializers.CharField()


class ChatbotResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    intent = serializers.CharField()
