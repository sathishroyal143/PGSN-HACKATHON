"""Support repositories."""
from django.utils import timezone
from .models import ChatbotLog, FAQ, Ticket, TicketMessage
from . import constants


class TicketRepository:

    @staticmethod
    def create(user_id, subject, description, category, priority):
        return Ticket.objects.create(
            user_id=user_id, subject=subject, description=description,
            category=category, priority=priority,
        )

    @staticmethod
    def get_by_id(ticket_id):
        return Ticket.objects.filter(id=ticket_id).first()

    @staticmethod
    def get_for_user(user_id):
        return Ticket.objects.filter(user_id=user_id).order_by('-created_at')

    @staticmethod
    def get_all():
        return Ticket.objects.select_related('user', 'assigned_to').order_by('-created_at')

    @staticmethod
    def update_status(ticket_id, status, resolution_notes=''):
        update = {'status': status}
        if status == constants.TICKET_STATUS_RESOLVED:
            update['resolved_at'] = timezone.now()
            if resolution_notes:
                update['resolution_notes'] = resolution_notes
        Ticket.objects.filter(id=ticket_id).update(**update)


class TicketMessageRepository:

    @staticmethod
    def create(ticket_id, sender_id, body, is_staff_reply=False):
        return TicketMessage.objects.create(
            ticket_id=ticket_id, sender_id=sender_id,
            body=body, is_staff_reply=is_staff_reply,
        )

    @staticmethod
    def get_for_ticket(ticket_id):
        return TicketMessage.objects.filter(ticket_id=ticket_id).order_by('created_at')


class FAQRepository:

    @staticmethod
    def get_published(category=None):
        qs = FAQ.objects.filter(is_published=True)
        if category:
            qs = qs.filter(category=category)
        return qs.order_by('category', 'order')

    @staticmethod
    def get_all():
        return FAQ.objects.order_by('category', 'order')


class ChatbotLogRepository:

    @staticmethod
    def create(user_id, user_message, bot_response, intent=''):
        return ChatbotLog.objects.create(
            user_id=user_id, user_message=user_message,
            bot_response=bot_response, intent=intent,
        )

    @staticmethod
    def get_for_user(user_id):
        return ChatbotLog.objects.filter(user_id=user_id).order_by('-created_at')
