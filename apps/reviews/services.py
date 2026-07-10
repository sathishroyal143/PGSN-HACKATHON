"""Reviews services."""
import logging
from .repositories import ComplaintRepository, ReviewReplyRepository, ReviewRepository
from .exceptions import ReviewAlreadyExistsException, ReviewNotFoundException, ReviewNotAllowedException
from . import constants

logger = logging.getLogger('carebridge')


class ReviewService:

    @staticmethod
    def submit(booking_id, reviewer_id, reviewee_id, rating, title='', comment='', is_anonymous=False):
        from apps.bookings.models import Booking
        from .models import Review
        if not Booking.objects.filter(id=booking_id, status='COMPLETED').exists():
            raise ReviewNotAllowedException('Booking must be completed to leave a review.')
        if Review.objects.filter(booking_id=booking_id, reviewer_id=reviewer_id).exists():
            raise ReviewAlreadyExistsException()
        review = ReviewRepository.create(
            booking_id, reviewer_id, reviewee_id, rating, title, comment, is_anonymous
        )
        logger.info('Review submitted review=%s booking=%s', review.id, booking_id)
        return review

    @staticmethod
    def reply(review_id, author_id, comment):
        review = ReviewRepository.get_by_id(review_id)
        if not review:
            raise ReviewNotFoundException()
        from .models import ReviewReply
        if ReviewReply.objects.filter(review_id=review_id).exists():
            from .exceptions import ReviewAlreadyExistsException
            raise ReviewAlreadyExistsException('A reply already exists for this review.')
        return ReviewReplyRepository.create(review_id, author_id, comment)


class ComplaintService:

    @staticmethod
    def file(booking_id, filed_by_id, against_id, subject, description, priority=constants.COMPLAINT_PRIORITY_MEDIUM):
        complaint = ComplaintRepository.create(booking_id, filed_by_id, against_id, subject, description, priority)
        logger.info('Complaint filed complaint=%s booking=%s', complaint.id, booking_id)
        return complaint
