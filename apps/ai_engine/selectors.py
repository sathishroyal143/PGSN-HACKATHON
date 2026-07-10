"""AI Engine selectors."""
from .repositories import AIRequestRepository, MatchScoreRepository


class AIRequestSelectors:

    @staticmethod
    def get_by_id(request_id):
        return AIRequestRepository.get_by_id(request_id)

    @staticmethod
    def for_user(user_id):
        return AIRequestRepository.get_for_user(user_id)


class MatchScoreSelectors:

    @staticmethod
    def for_request(request_id):
        return MatchScoreRepository.get_for_request(request_id)
