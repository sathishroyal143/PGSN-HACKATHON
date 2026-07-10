"""Support selectors."""
from .repositories import FAQRepository, TicketMessageRepository, TicketRepository


class TicketSelectors:

    @staticmethod
    def for_user(user_id):
        return TicketRepository.get_for_user(user_id)

    @staticmethod
    def all_tickets():
        return TicketRepository.get_all()

    @staticmethod
    def messages(ticket_id):
        return TicketMessageRepository.get_for_ticket(ticket_id)


class FAQSelectors:

    @staticmethod
    def published(category=None):
        return FAQRepository.get_published(category)
