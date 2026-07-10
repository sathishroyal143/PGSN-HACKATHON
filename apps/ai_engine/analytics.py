"""AI Engine analytics — usage statistics aggregator."""
from django.db.models import Count, Avg, Q
from .models import AIRequest
from . import constants


def get_usage_stats(user_id=None) -> dict:
    """
    Return AI request usage statistics.
    If user_id provided, scoped to that user; otherwise platform-wide (admin use).
    """
    qs = AIRequest.objects.all()
    if user_id:
        qs = qs.filter(user_id=user_id)

    total = qs.count()
    by_type = dict(
        qs.values('request_type')
          .annotate(count=Count('id'))
          .values_list('request_type', 'count')
    )
    by_status = dict(
        qs.values('status')
          .annotate(count=Count('id'))
          .values_list('status', 'count')
    )
    avg_processing = qs.filter(
        status=constants.STATUS_COMPLETED,
        processing_time_ms__isnull=False,
    ).aggregate(avg=Avg('processing_time_ms'))['avg']

    return {
        'total_requests': total,
        'by_type': by_type,
        'by_status': by_status,
        'avg_processing_ms': round(avg_processing or 0, 1),
        'success_rate': round(
            (by_status.get(constants.STATUS_COMPLETED, 0) / total * 100) if total else 0, 1
        ),
    }


def get_match_quality_stats() -> dict:
    """Return average match scores across all companion match requests."""
    from .models import MatchScore
    from django.db.models import Avg

    agg = MatchScore.objects.filter(rank=1).aggregate(
        avg_total=Avg('total_score'),
        avg_rating=Avg('rating_score'),
        avg_skills=Avg('skills_score'),
        avg_trust=Avg('trust_score'),
    )
    return {k: round(v or 0, 2) for k, v in agg.items()}
