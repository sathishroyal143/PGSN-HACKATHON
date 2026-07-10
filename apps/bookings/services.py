"""Bookings business logic."""
import logging
from django.utils import timezone
from common.exceptions import ValidationException, ResourceNotFoundException, BusinessLogicException
from .models import Booking, BookingStatusLog
from .repositories import BookingRepository
from . import constants

logger = logging.getLogger('carebridge')

# Valid status transitions
TRANSITIONS = {
    constants.STATUS_PENDING: [constants.STATUS_CONFIRMED, constants.STATUS_CANCELLED, constants.STATUS_COMPANION_ASSIGNED],
    constants.STATUS_CONFIRMED: [constants.STATUS_COMPANION_ASSIGNED, constants.STATUS_CANCELLED],
    constants.STATUS_COMPANION_ASSIGNED: [constants.STATUS_IN_PROGRESS, constants.STATUS_CANCELLED],
    constants.STATUS_IN_PROGRESS: [constants.STATUS_COMPLETED, constants.STATUS_FAILED],
    constants.STATUS_COMPLETED: [],
    constants.STATUS_CANCELLED: [],
    constants.STATUS_FAILED: [],
}


class BookingService:
    @staticmethod
    def create_booking(data: dict, family_user) -> Booking:
        from apps.services.models import CareService
        from apps.services.selectors import ServiceSelectors

        care_service = None
        package = None
        service_name_snapshot = ''
        breakdown = {}

        # ── Resolve service reference ──────────────────────────────────────────
        if data.get('care_service_id'):
            care_service = CareService.objects.filter(
                id=data['care_service_id'], is_deleted=False
            ).select_related('service_category').prefetch_related('pricing_history').first()
            if not care_service:
                raise ResourceNotFoundException("Care service not found.")
            service_name_snapshot = care_service.service_name

            # Calculate price from CareService pricing
            hours = (data['scheduled_end'] - data['scheduled_start']).total_seconds() / 3600
            is_emergency = data.get('booking_type') == constants.BOOKING_TYPE_EMERGENCY
            pricing = care_service.pricing_history.filter(is_active=True).order_by('-effective_from').first()
            if pricing:
                breakdown = pricing.calculate_total(hours, is_emergency)
            else:
                from decimal import Decimal
                base = float(care_service.base_price)
                breakdown = {'base_price': base, 'total': base}

        elif data.get('service_package_id'):
            package = ServiceSelectors.get_package_detail(data['service_package_id'])
            if not package:
                raise ResourceNotFoundException("Service package not found.")
            service_name_snapshot = package.name
            hours = (data['scheduled_end'] - data['scheduled_start']).total_seconds() / 3600
            is_emergency = data.get('booking_type') == constants.BOOKING_TYPE_EMERGENCY
            breakdown = package.pricing.calculate_total(hours, is_emergency) if hasattr(package, 'pricing') else {}
        else:
            raise ValidationException("Either care_service_id or service_package_id is required.")

        # ── Time validation (Emergency/Instant bypass future-time check) ────────
        booking_type = data.get('booking_type', constants.BOOKING_TYPE_SCHEDULED)
        if booking_type == constants.BOOKING_TYPE_SCHEDULED:
            if data['scheduled_start'] <= timezone.now():
                raise ValidationException("Scheduled start must be in the future for scheduled bookings.")
        if data['scheduled_end'] <= data['scheduled_start']:
            raise ValidationException("Scheduled end must be after start.")

        booking = Booking.objects.create(
            family_user=family_user,
            patient_id=data['patient_id'],
            care_service=care_service,
            service_package=package,
            service_name=service_name_snapshot,
            booking_type=booking_type,
            scheduled_start=data['scheduled_start'],
            scheduled_end=data['scheduled_end'],
            pickup_address=data['pickup_address'],
            pickup_latitude=data.get('pickup_latitude'),
            pickup_longitude=data.get('pickup_longitude'),
            hospital_name=data.get('hospital_name', ''),
            hospital_address=data.get('hospital_address', ''),
            hospital_latitude=data.get('hospital_latitude'),
            hospital_longitude=data.get('hospital_longitude'),
            special_instructions=data.get('special_instructions', ''),
            requires_wheelchair=data.get('requires_wheelchair', False),
            requires_oxygen=data.get('requires_oxygen', False),
            quoted_price=breakdown.get('total', 0),
            price_breakdown=breakdown,
        )
        BookingStatusLog.objects.create(
            booking=booking,
            from_status='',
            to_status=constants.STATUS_PENDING,
            changed_by=family_user,
            notes='Booking created.',
        )
        logger.info(f"Booking created: {booking.id} by user {family_user.id}")
        return booking


    @staticmethod
    def transition_status(booking_id, new_status: str, changed_by, notes: str = '') -> Booking:
        booking = BookingRepository.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException("Booking not found.")

        allowed = TRANSITIONS.get(booking.status, [])
        if new_status not in allowed:
            raise BusinessLogicException(
                f"Cannot transition from '{booking.status}' to '{new_status}'."
            )

        old_status = booking.status
        booking.status = new_status

        if new_status == constants.STATUS_IN_PROGRESS:
            booking.actual_start = timezone.now()
            # Auto-create CareJourney if not exists
            from apps.care_journey.services import CareJourneyService
            try:
                CareJourneyService.start_journey(booking.id, changed_by)
            except Exception as e:
                logger.warning(f"Failed to auto-start CareJourney: {e}")
        elif new_status in [constants.STATUS_COMPLETED, constants.STATUS_FAILED]:
            booking.actual_end = timezone.now()
            if new_status == constants.STATUS_COMPLETED:
                booking.final_price = booking.quoted_price
        elif new_status == constants.STATUS_CANCELLED:
            booking.cancelled_at = timezone.now()

        booking.save()
        BookingStatusLog.objects.create(
            booking=booking,
            from_status=old_status,
            to_status=new_status,
            changed_by=changed_by,
            notes=notes,
        )
        logger.info(f"Booking {booking.id} transitioned: {old_status} → {new_status}")
        return booking

    @staticmethod
    def assign_companion(booking_id, companion, changed_by) -> Booking:
        booking = BookingRepository.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException("Booking not found.")
        if booking.status not in [constants.STATUS_PENDING, constants.STATUS_CONFIRMED]:
            raise BusinessLogicException("Companion can only be assigned to pending/confirmed bookings.")

        booking.companion = companion
        booking.status = constants.STATUS_COMPANION_ASSIGNED
        booking.save(update_fields=['companion', 'status', 'updated_at'])
        BookingStatusLog.objects.create(
            booking=booking,
            from_status=constants.STATUS_CONFIRMED,
            to_status=constants.STATUS_COMPANION_ASSIGNED,
            changed_by=changed_by,
            notes=f"Companion {companion.get_full_name()} assigned.",
        )
        return booking

    @staticmethod
    def cancel_booking(booking_id, cancelled_by_user, reason: str, cancel_by: str) -> Booking:
        booking = BookingRepository.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException("Booking not found.")
        if booking.status in [constants.STATUS_COMPLETED, constants.STATUS_CANCELLED]:
            raise BusinessLogicException("Cannot cancel a completed or already cancelled booking.")

        old_status = booking.status
        booking.status = constants.STATUS_CANCELLED
        booking.cancelled_at = timezone.now()
        booking.cancelled_by = cancel_by
        booking.cancellation_reason = reason
        booking.save()
        BookingStatusLog.objects.create(
            booking=booking,
            from_status=old_status,
            to_status=constants.STATUS_CANCELLED,
            changed_by=cancelled_by_user,
            notes=reason,
        )
        return booking

    @staticmethod
    def accept_booking(booking_id, companion) -> Booking:
        booking = BookingRepository.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException("Booking not found.")
        if booking.companion is not None:
            raise BusinessLogicException("Booking already has an assigned companion.")
        if booking.status not in [constants.STATUS_PENDING, constants.STATUS_CONFIRMED]:
            raise BusinessLogicException("Booking is not in a state that can be accepted.")

        old_status = booking.status
        booking.companion = companion
        booking.status = constants.STATUS_IN_PROGRESS
        booking.actual_start = timezone.now()
        booking.save(update_fields=['companion', 'status', 'actual_start', 'updated_at'])

        BookingStatusLog.objects.create(
            booking=booking,
            from_status=old_status,
            to_status=constants.STATUS_IN_PROGRESS,
            changed_by=companion,
            notes=f"Companion {companion.get_full_name()} accepted the booking and started the journey.",
        )
        logger.info(f"Booking {booking.id} accepted by companion {companion.id}")

        # Auto-create CareJourney immediately upon acceptance
        from apps.care_journey.services import CareJourneyService
        try:
            CareJourneyService.start_journey(booking.id, companion)
        except Exception as e:
            logger.warning(f"Failed to auto-start CareJourney upon acceptance: {e}")

        return booking

    @staticmethod
    def reject_booking(booking_id, companion, reason: str = '') -> Booking:
        booking = BookingRepository.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException("Booking not found.")

        BookingStatusLog.objects.create(
            booking=booking,
            from_status=booking.status,
            to_status=booking.status,
            changed_by=companion,
            notes=f"Companion {companion.get_full_name()} rejected request. Reason: {reason}",
        )
        logger.info(f"Booking {booking.id} rejected by companion {companion.id}")
        return booking

