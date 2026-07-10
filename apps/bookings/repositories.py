"""Bookings repositories."""
from django.db.models import Q
from .models import Booking, BookingStatusLog
from . import constants


class BookingRepository:
    @staticmethod
    def get_by_id(pk):
        return Booking.objects.select_related(
            'family_user', 'patient', 'companion', 'service_package', 'care_service'
        ).filter(pk=pk).first()

    @staticmethod
    def get_family_bookings(user_id, status=None):
        qs = Booking.objects.select_related(
            'patient', 'companion', 'service_package', 'care_service'
        ).filter(family_user_id=user_id)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')

    @staticmethod
    def get_companion_bookings(companion_id, status=None):
        qs = Booking.objects.select_related(
            'patient', 'family_user', 'service_package', 'care_service'
        ).filter(companion_id=companion_id)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-scheduled_start')

    @staticmethod
    def get_pending_unassigned():
        return Booking.objects.filter(
            status=constants.STATUS_PENDING,
            companion__isnull=True,
        ).select_related('patient', 'service_package', 'care_service', 'family_user')

    @staticmethod
    def get_active_bookings():
        return Booking.objects.filter(
            status__in=[constants.STATUS_CONFIRMED, constants.STATUS_COMPANION_ASSIGNED, constants.STATUS_IN_PROGRESS],
        )

