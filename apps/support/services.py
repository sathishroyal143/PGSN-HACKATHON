"""Support services."""
import logging
from .repositories import ChatbotLogRepository, TicketMessageRepository, TicketRepository
from .exceptions import TicketNotFoundException
from . import constants

logger = logging.getLogger('carebridge')


class TicketService:

    @staticmethod
    def create(user_id, subject, description, category=constants.TICKET_CATEGORY_OTHER,
               priority=constants.TICKET_PRIORITY_MEDIUM):
        ticket = TicketRepository.create(user_id, subject, description, category, priority)
        logger.info('Support ticket created ticket=%s user=%s', ticket.id, user_id)
        return ticket

    @staticmethod
    def reply(ticket_id, sender_id, body, is_staff_reply=False):
        ticket = TicketRepository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException()
        msg = TicketMessageRepository.create(ticket_id, sender_id, body, is_staff_reply)
        if ticket.status == constants.TICKET_STATUS_OPEN and not is_staff_reply:
            pass  # keep open
        elif is_staff_reply and ticket.status == constants.TICKET_STATUS_OPEN:
            TicketRepository.update_status(ticket_id, constants.TICKET_STATUS_IN_PROGRESS)
        return msg

    @staticmethod
    def resolve(ticket_id, resolution_notes=''):
        ticket = TicketRepository.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundException()
        TicketRepository.update_status(ticket_id, constants.TICKET_STATUS_RESOLVED, resolution_notes)
        logger.info('Ticket resolved ticket=%s', ticket_id)


class ChatbotService:

    # Simple keyword-based bot — no external API needed
    _RESPONSES = {
        'booking': ('booking', 'You can manage your bookings under the Bookings section. Need more help?'),
        'payment': ('payment', 'For payment issues, visit the Payments section or contact support.'),
        'cancel': ('cancellation', 'To cancel a booking, go to Booking Detail and tap Cancel.'),
        'companion': ('companion', 'Browse available companions in the Companions section.'),
        'password': ('account', 'Use Forgot Password on the login page to reset your password.'),
        'refund': ('refund', 'Refund requests can be raised from the Payments section.'),
    }
    _DEFAULT = ('general', "I'm here to help! Please describe your issue or raise a support ticket.")

    @classmethod
    def respond(cls, user_id, message):
        lower = message.lower()
        intent, response = cls._DEFAULT
        for keyword, (kw_intent, kw_response) in cls._RESPONSES.items():
            if keyword in lower:
                intent, response = kw_intent, kw_response
                break
        ChatbotLogRepository.create(user_id, message, response, intent)
        return response, intent
