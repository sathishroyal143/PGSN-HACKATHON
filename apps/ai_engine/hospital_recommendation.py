"""Hospital recommendation engine — rule-based, proximity + specialty matching."""
from .route_optimizer import haversine_km


def recommend_hospitals(hospitals: list, patient_lat, patient_lon,
                         required_specialty: str = None, top_n: int = 5) -> list:
    """
    Rank hospitals by proximity and specialty match.

    hospitals: list of dicts with keys:
        id, name, address, latitude, longitude, specialties (list), emergency (bool)

    Returns list of dicts sorted by score desc (proximity + specialty bonus).
    """
    scored = []
    for h in hospitals:
        try:
            dist = haversine_km(patient_lat, patient_lon, h['latitude'], h['longitude'])
        except (KeyError, TypeError, ValueError):
            continue

        # Proximity score: 100 at 0 km, 0 at 50 km
        proximity_score = max(0.0, 100.0 - (dist / 50.0) * 100.0)

        # Specialty match bonus
        specialty_bonus = 0.0
        if required_specialty:
            specialties = [s.lower() for s in h.get('specialties', [])]
            if required_specialty.lower() in specialties:
                specialty_bonus = 30.0

        # Emergency bonus
        emergency_bonus = 10.0 if h.get('emergency') else 0.0

        total = round(proximity_score + specialty_bonus + emergency_bonus, 2)
        scored.append({**h, 'distance_km': round(dist, 2), 'score': total})

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_n]
