"""Bookings selectors."""
from .repositories import BookingRepository


class BookingSelectors:
    @staticmethod
    def get_booking(pk):
        return BookingRepository.get_by_id(pk)

    @staticmethod
    def family_bookings(user_id, status=None):
        return BookingRepository.get_family_bookings(user_id, status)

    @staticmethod
    def companion_bookings(companion_id, status=None):
        return BookingRepository.get_companion_bookings(companion_id, status)

    @staticmethod
    def pending_unassigned():
        return BookingRepository.get_pending_unassigned()
