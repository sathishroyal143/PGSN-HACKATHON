"""Care Journey selectors."""
from .repositories import CareJourneyRepository


class CareJourneySelectors:
    @staticmethod
    def get_journey(pk):
        return CareJourneyRepository.get_by_id(pk)

    @staticmethod
    def get_by_booking(booking_id):
        return CareJourneyRepository.get_by_booking(booking_id)

    @staticmethod
    def get_active_journeys():
        return CareJourneyRepository.get_active_journeys()
