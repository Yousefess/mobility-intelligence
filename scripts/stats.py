import math
from dataclasses import dataclass

from scripts.geolife_parser import RawPoint

EARTH_RADIUS_M = 6_371_000


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in meters."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_M * c


@dataclass
class TrajectoryStats:
    distance_m: float
    duration_s: int
    avg_speed_mps: float


def compute_stats(points: list[RawPoint]) -> TrajectoryStats:
    total_distance = 0.0
    for prev, curr in zip(points, points[1:]):
        total_distance += haversine_m(prev.lat, prev.lon, curr.lat, curr.lon)

    duration_s = int((points[-1].timestamp - points[0].timestamp).total_seconds())
    avg_speed = total_distance / duration_s if duration_s > 0 else 0.0

    return TrajectoryStats(
        distance_m=total_distance, duration_s=duration_s, avg_speed_mps=avg_speed
    )
