"""Geofence utility — Haversine-based point-in-circle check."""
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Returns the great-circle distance in meters between two GPS coordinates.
    Uses the Haversine formula.
    """
    R = 6_371_000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def is_inside_geofence(lat: float, lon: float, fence_lat: float, fence_lon: float, radius_meters: float) -> bool:
    """Returns True if the point (lat, lon) is within radius_meters of the fence centre."""
    return haversine_distance(lat, lon, fence_lat, fence_lon) <= radius_meters
