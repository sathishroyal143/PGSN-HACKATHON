"""Reviews selectors."""
from .repositories import ComplaintRepository, ReviewRepository


class ReviewSelectors:

    @staticmethod
    def for_reviewee(reviewee_id):
        return ReviewRepository.get_for_reviewee(reviewee_id)

    @staticmethod
    def by_reviewer(reviewer_id):
        return ReviewRepository.get_by_reviewer(reviewer_id)

    @staticmethod
    def average_rating(reviewee_id):
        return ReviewRepository.average_rating(reviewee_id)


class ComplaintSelectors:

    @staticmethod
    def for_user(user_id):
        return ComplaintRepository.get_for_user(user_id)
