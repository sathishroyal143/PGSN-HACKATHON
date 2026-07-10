"""Trust score calculator — rule-based, no external API needed."""


def compute_trust_score(companion):
    """
    Compute a 0–100 trust score for a CompanionProfile.
    Factors: rating, completed bookings, KYC status, experience.
    """
    score = 0.0

    # Rating (0–5) → 0–40 pts
    score += (float(companion.average_rating) / 5.0) * 40

    # Completed bookings (capped at 100) → 0–20 pts
    score += min(companion.total_bookings_completed / 100, 1.0) * 20

    # Experience years (capped at 10) → 0–20 pts
    score += min(companion.experience_years / 10, 1.0) * 20

    # KYC verified → 0 or 20 pts
    try:
        if companion.user.kyc_record and companion.user.kyc_record.is_verified:
            score += 20
    except Exception:
        pass

    return round(min(score, 100.0), 2)
