"""Care Journey business logic."""
import logging
from django.utils import timezone
from common.exceptions import ValidationException, ResourceNotFoundException, BusinessLogicException
from .models import CareJourney, JourneyStep
from .repositories import CareJourneyRepository
from . import constants

logger = logging.getLogger('carebridge')

STEP_TRANSITIONS = {
    constants.STEP_STATUS_PENDING: [constants.STEP_STATUS_IN_PROGRESS],
    constants.STEP_STATUS_IN_PROGRESS: [constants.STEP_STATUS_DONE],
    constants.STEP_STATUS_DONE: [],
}


class CareJourneyService:
    @staticmethod
    def start_journey(booking_id, started_by) -> CareJourney:
        existing = CareJourneyRepository.get_by_booking(booking_id)
        if existing:
            raise BusinessLogicException("Journey already exists for this booking.")

        journey = CareJourney.objects.create(
            booking_id=booking_id,
            status=constants.JOURNEY_STATUS_ACTIVE,
            current_step=constants.STEP_ACCEPTED,
            started_at=timezone.now(),
        )
        steps = [
            JourneyStep(
                journey=journey,
                step_code=code,
                step_order=i,
                status=constants.STEP_STATUS_PENDING,
            )
            for i, code in enumerate(constants.STEP_ORDER)
        ]
        JourneyStep.objects.bulk_create(steps)
        logger.info(f"Journey {journey.id} started for booking {booking_id}")
        return CareJourneyRepository.get_by_id(journey.id)

    @staticmethod
    def advance_step(journey_id, step_code: str, new_status: str, updated_by, notes: str = '') -> CareJourney:
        journey = CareJourneyRepository.get_by_id(journey_id)
        if not journey:
            raise ResourceNotFoundException("Journey not found.")
        if journey.status != constants.JOURNEY_STATUS_ACTIVE:
            raise BusinessLogicException("Journey is not active.")

        step = journey.steps.filter(step_code=step_code).first()
        if not step:
            raise ResourceNotFoundException(f"Step '{step_code}' not found.")

        allowed = STEP_TRANSITIONS.get(step.status, [])
        if new_status not in allowed:
            raise BusinessLogicException(
                f"Cannot transition step from '{step.status}' to '{new_status}'."
            )

        step.status = new_status
        step.notes = notes
        step.updated_by = updated_by
        if new_status == constants.STEP_STATUS_IN_PROGRESS:
            step.started_at = timezone.now()
        elif new_status == constants.STEP_STATUS_DONE:
            step.completed_at = timezone.now()
            
        # Send Notification to Family User
        from apps.notifications.services import NotificationService
        from apps.notifications import constants as notif_constants
        
        try:
            family_user = journey.booking.family_user
            step_name = dict(constants.JOURNEY_STEPS).get(step.step_code, step.step_code)
            status_text = "is in progress" if new_status == constants.STEP_STATUS_IN_PROGRESS else "is completed"
            NotificationService.send(
                user_id=family_user.id,
                notification_type=notif_constants.TYPE_JOURNEY_UPDATE,
                title="Care Journey Update",
                body=f"Step '{step_name}' for {journey.booking.patient.first_name} {status_text}.",
                channel=notif_constants.CHANNEL_IN_APP,
                data={'journey_id': str(journey.id), 'booking_id': str(journey.booking.id)},
                action_url=f"/family/bookings/{journey.booking.id}"
            )
            step.family_notified = True
        except Exception as e:
            logger.warning(f"Failed to send journey update notification: {e}")

        step.save()

        # Advance current_step pointer to next pending or in-progress step
        remaining_step = journey.steps.exclude(
            status=constants.STEP_STATUS_DONE,
        ).order_by('step_order').first()
        if remaining_step:
            journey.current_step = remaining_step.step_code
        else:
            # All steps done — complete journey
            journey.status = constants.JOURNEY_STATUS_COMPLETED
            journey.current_step = constants.STEP_JOURNEY_COMPLETED
            journey.completed_at = timezone.now()
            
            # Update booking to COMPLETED
            booking = journey.booking
            old_booking_status = booking.status
            booking.status = 'COMPLETED'  # using string as constants might not be imported from bookings here
            booking.actual_end = timezone.now()
            booking.save(update_fields=['status', 'actual_end', 'updated_at'])
            
            from apps.bookings.models import BookingStatusLog
            BookingStatusLog.objects.create(
                booking=booking,
                from_status=old_booking_status,
                to_status='COMPLETED',
                changed_by=updated_by,
                notes="Care Journey completed.",
            )
            
            # --- Escrow Wallet Transfer ---
            from apps.payments.services import WalletService
            from apps.payments.exceptions import InsufficientWalletBalanceException
            try:
                WalletService.transfer_funds(
                    sender_id=booking.family_user_id,
                    receiver_id=booking.companion_id,
                    amount=booking.quoted_price,
                    description=f"Journey {journey.id}",
                    reference_id=str(booking.id)
                )
                logger.info(f"Escrow transfer successful for Journey {journey.id}")
            except InsufficientWalletBalanceException:
                logger.error(f"Escrow transfer failed for Journey {journey.id}: Insufficient balance.")
                # We could potentially mark the journey as pending payment here if needed,
                # but per requirements, they must have balance before booking anyway.
                raise BusinessLogicException("Insufficient wallet balance for payment transfer.")
            except Exception as e:
                logger.error(f"Escrow transfer failed with error: {e}")
                raise BusinessLogicException("Failed to process payment transfer.")
            
            # Close the associated conversation
            if hasattr(booking, 'conversation') and booking.conversation:
                booking.conversation.status = 'closed'
                booking.conversation.save(update_fields=['status', 'updated_at'])

        journey.save()

        logger.info(f"Journey {journey_id} step {step_code} → {new_status}")
        return CareJourneyRepository.get_by_id(journey_id)

    @staticmethod
    def update_notes(journey_id, notes: str, updated_by) -> CareJourney:
        journey = CareJourneyRepository.get_by_id(journey_id)
        if not journey:
            raise ResourceNotFoundException("Journey not found.")
        journey.companion_notes = notes
        journey.save(update_fields=['companion_notes', 'updated_at'])
        return journey

    @staticmethod
    def cancel_journey(journey_id, cancelled_by) -> CareJourney:
        journey = CareJourneyRepository.get_by_id(journey_id)
        if not journey:
            raise ResourceNotFoundException("Journey not found.")
        if journey.status != constants.JOURNEY_STATUS_ACTIVE:
            raise BusinessLogicException("Only active journeys can be cancelled.")
        journey.status = constants.JOURNEY_STATUS_CANCELLED
        journey.save(update_fields=['status', 'updated_at'])
        return journey
