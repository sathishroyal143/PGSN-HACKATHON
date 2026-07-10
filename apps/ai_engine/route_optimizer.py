"""Route optimizer — ranks companions by proximity using Haversine distance."""
import math


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Return great-circle distance in km between two coordinates."""
    R = 6371.0
    phi1, phi2 = math.radians(float(lat1)), math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlam = math.radians(float(lon2) - float(lon1))
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def rank_by_proximity(companions, patient_lat, patient_lon, max_radius_km=None):
    """
    Sort companions by distance to patient location.
    companions: queryset of CompanionProfile with current_latitude/current_longitude set.
    Returns list of (companion, distance_km) sorted nearest first.
    Excludes companions with no location data.
    """
    results = []
    for companion in companions:
        if companion.current_latitude is None or companion.current_longitude is None:
            continue
        dist = haversine_km(
            patient_lat, patient_lon,
            companion.current_latitude, companion.current_longitude,
        )
        if max_radius_km is None or dist <= max_radius_km:
            results.append((companion, round(dist, 2)))

    results.sort(key=lambda x: x[1])
    return results


def nearest_companion(companions, patient_lat, patient_lon):
    """Return the single nearest companion or None."""
    ranked = rank_by_proximity(companions, patient_lat, patient_lon)
    return ranked[0] if ranked else None
