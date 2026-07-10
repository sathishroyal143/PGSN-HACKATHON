"""Live Tracking permissions."""
from rest_framework.permissions import BasePermission

from apps.bookings.models import Booking


def _get_booking(view) -> Booking | None:
    booking_id = view.kwargs.get('booking_id')
    if not booking_id:
        return None
    return Booking.objects.filter(id=booking_id, is_deleted=False).first()


class IsCompanionOfBooking(BasePermission):
    """
    Grants write access only to the companion assigned to the booking.
    Used for location update endpoints.
    """
    message = 'Only the assigned companion can post location updates.'

    def has_permission(self, request, view):
        booking = _get_booking(view)
        if not booking:
            return False
        return booking.companion_id == request.user.id


class IsBookingParticipant(BasePermission):
    """
    Grants read access to the family user, the assigned companion, or admin/support.
    Used for tracking read endpoints.
    """
    message = 'You are not a participant of this booking.'

    def has_permission(self, request, view):
        from apps.users.models import UserRole
        if request.user.role in (UserRole.ADMIN, UserRole.SUPPORT):
            return True
        booking = _get_booking(view)
        if not booking:
            return False
        return request.user.id in (booking.family_user_id, booking.companion_id)
