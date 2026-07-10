"""Reviews repositories."""
from django.db.models import Avg
from .models import Complaint, Review, ReviewReply
from . import constants


class ReviewRepository:

    @staticmethod
    def create(booking_id, reviewer_id, reviewee_id, rating, title='', comment='', is_anonymous=False):
        return Review.objects.create(
            booking_id=booking_id, reviewer_id=reviewer_id, reviewee_id=reviewee_id,
            rating=rating, title=title, comment=comment, is_anonymous=is_anonymous,
        )

    @staticmethod
    def get_by_id(review_id):
        return Review.objects.filter(id=review_id).first()

    @staticmethod
    def get_for_reviewee(reviewee_id):
        return Review.objects.filter(
            reviewee_id=reviewee_id, status=constants.REVIEW_STATUS_APPROVED
        ).order_by('-created_at')

    @staticmethod
    def get_by_reviewer(reviewer_id):
        return Review.objects.filter(reviewer_id=reviewer_id).order_by('-created_at')

    @staticmethod
    def average_rating(reviewee_id):
        result = Review.objects.filter(
            reviewee_id=reviewee_id, status=constants.REVIEW_STATUS_APPROVED
        ).aggregate(avg=Avg('rating'))
        return round(result['avg'] or 0, 2)


class ReviewReplyRepository:

    @staticmethod
    def create(review_id, author_id, comment):
        return ReviewReply.objects.create(review_id=review_id, author_id=author_id, comment=comment)

    @staticmethod
    def get_for_review(review_id):
        return ReviewReply.objects.filter(review_id=review_id).first()


class ComplaintRepository:

    @staticmethod
    def create(booking_id, filed_by_id, against_id, subject, description, priority=constants.COMPLAINT_PRIORITY_MEDIUM):
        return Complaint.objects.create(
            booking_id=booking_id, filed_by_id=filed_by_id, against_id=against_id,
            subject=subject, description=description, priority=priority,
        )

    @staticmethod
    def get_by_id(complaint_id):
        return Complaint.objects.filter(id=complaint_id).first()

    @staticmethod
    def get_for_user(user_id):
        return Complaint.objects.filter(filed_by_id=user_id).order_by('-created_at')

    @staticmethod
    def resolve(complaint_id, resolution_notes):
        from django.utils import timezone
        Complaint.objects.filter(id=complaint_id).update(
            status=constants.COMPLAINT_STATUS_RESOLVED,
            resolution_notes=resolution_notes,
            resolved_at=timezone.now(),
        )
