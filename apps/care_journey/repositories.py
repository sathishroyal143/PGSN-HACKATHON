"""Care Journey repositories."""
from .models import CareJourney, JourneyStep


class CareJourneyRepository:
    @staticmethod
    def get_by_id(pk):
        return CareJourney.objects.select_related('booking').prefetch_related('steps').filter(pk=pk).first()

    @staticmethod
    def get_by_booking(booking_id):
        return CareJourney.objects.prefetch_related('steps').filter(booking_id=booking_id).first()

    @staticmethod
    def get_active_journeys():
        from . import constants
        return CareJourney.objects.filter(status=constants.JOURNEY_STATUS_ACTIVE).select_related('booking')
