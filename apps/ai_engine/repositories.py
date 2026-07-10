"""AI Engine repositories."""
from .models import AIRequest, AIResponse, MatchScore
from . import constants


class AIRequestRepository:

    @staticmethod
    def create(user_id, request_type, input_data):
        return AIRequest.objects.create(
            user_id=user_id,
            request_type=request_type,
            input_data=input_data,
            status=constants.STATUS_PENDING,
        )

    @staticmethod
    def get_by_id(request_id):
        return AIRequest.objects.filter(id=request_id).select_related('response').first()

    @staticmethod
    def get_for_user(user_id):
        return AIRequest.objects.filter(user_id=user_id).select_related('response').order_by('-created_at')

    @staticmethod
    def mark_processing(request_id):
        AIRequest.objects.filter(id=request_id).update(status=constants.STATUS_PROCESSING)

    @staticmethod
    def mark_completed(request_id, processing_time_ms=None):
        AIRequest.objects.filter(id=request_id).update(
            status=constants.STATUS_COMPLETED,
            processing_time_ms=processing_time_ms,
        )

    @staticmethod
    def mark_failed(request_id, error_message):
        AIRequest.objects.filter(id=request_id).update(
            status=constants.STATUS_FAILED,
            error_message=error_message,
        )


class AIResponseRepository:

    @staticmethod
    def create(request_id, output_data, model_used='rule_based', tokens_used=0):
        return AIResponse.objects.create(
            request_id=request_id,
            output_data=output_data,
            model_used=model_used,
            tokens_used=tokens_used,
        )


class MatchScoreRepository:

    @staticmethod
    def bulk_create(request_id, ranked_companions):
        """ranked_companions: list of (companion, scores_dict) sorted by rank."""
        objs = []
        for rank, (companion, scores) in enumerate(ranked_companions, start=1):
            objs.append(MatchScore(
                request_id=request_id,
                companion=companion,
                rank=rank,
                total_score=scores['total_score'],
                rating_score=scores['rating_score'],
                skills_score=scores['skills_score'],
                experience_score=scores['experience_score'],
                trust_score=scores['trust_score'],
                availability_score=scores['availability_score'],
            ))
        return MatchScore.objects.bulk_create(objs)

    @staticmethod
    def get_for_request(request_id):
        return MatchScore.objects.filter(request_id=request_id).select_related(
            'companion', 'companion__user'
        ).order_by('rank')
