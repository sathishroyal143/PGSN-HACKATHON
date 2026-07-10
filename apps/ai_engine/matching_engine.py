"""Companion matching engine — rule-based scoring."""
from . import constants


def _skill_overlap_score(companion_skills, required_skills):
    """Returns 0–100 based on how many required skills the companion has."""
    if not required_skills:
        return 100.0
    companion_set = {s.skill for s in companion_skills}
    matched = len(set(required_skills) & companion_set)
    return round((matched / len(required_skills)) * 100, 2)


def _experience_score(years):
    """Maps experience years to 0–100."""
    if years >= 10:
        return 100.0
    return round((years / 10) * 100, 2)


def _rating_score(avg_rating):
    """Maps 0–5 rating to 0–100."""
    return round((float(avg_rating) / 5.0) * 100, 2)


def _trust_score_normalized(ai_trust_score):
    """ai_trust_score is already 0–100."""
    return round(float(ai_trust_score), 2)


def _availability_score(companion):
    """100 if online/available, 50 if offline, 0 if busy."""
    status = companion.availability_status
    if status == 'available':
        return 100.0
    if status == 'offline':
        return 50.0
    return 0.0


def score_companion(companion, required_skills=None):
    """
    Returns a dict of component scores and total weighted score (0–100).
    """
    skills = list(companion.skills.all())
    r = _rating_score(companion.average_rating)
    s = _skill_overlap_score(skills, required_skills or [])
    e = _experience_score(companion.experience_years)
    t = _trust_score_normalized(companion.ai_trust_score)
    a = _availability_score(companion)

    total = (
        r * constants.WEIGHT_RATING +
        s * constants.WEIGHT_SKILLS +
        e * constants.WEIGHT_EXPERIENCE +
        t * constants.WEIGHT_TRUST_SCORE +
        a * constants.WEIGHT_AVAILABILITY
    )

    return {
        'rating_score': round(r, 2),
        'skills_score': round(s, 2),
        'experience_score': round(e, 2),
        'trust_score': round(t, 2),
        'availability_score': round(a, 2),
        'total_score': round(total, 2),
    }


def rank_companions(companions, required_skills=None, top_n=10):
    """
    Score and rank a queryset of CompanionProfile objects.
    Returns list of (companion, scores_dict) sorted by total_score desc.
    """
    scored = []
    for companion in companions:
        scores = score_companion(companion, required_skills)
        scored.append((companion, scores))
    scored.sort(key=lambda x: x[1]['total_score'], reverse=True)
    return scored[:top_n]
