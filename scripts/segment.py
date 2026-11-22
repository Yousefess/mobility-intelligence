from dataclasses import dataclass
from datetime import timedelta

from scripts.geolife_parser import RawPoint

GAP_THRESHOLD = timedelta(minutes=20)


@dataclass
class Segment:
    points: list[RawPoint]


def segment_points(points: list[RawPoint]) -> list[Segment]:
    """Split a list of time-ordered points into segments wherever the gap
    between two consecutive points exceeds GAP_THRESHOLD.

    Within a single .plt file this acts as a safety net: GeoLife usually
    starts a new file per session, but a file can still contain an internal
    gap (GPS lost signal without a new file being started).
    """
    if not points:
        return []

    segments: list[Segment] = []
    current: list[RawPoint] = [points[0]]

    for prev, curr in zip(points, points[1:]):
        gap = curr.timestamp - prev.timestamp
        if gap > GAP_THRESHOLD:
            segments.append(Segment(points=current))
            current = [curr]
        else:
            current.append(curr)

    segments.append(Segment(points=current))

    # drop degenerate segments (a single point can't form a trajectory line)
    return [s for s in segments if len(s.points) >= 2]


if __name__ == "__main__":
    from geolife_parser import parse_plt_file

    points = parse_plt_file(
        "data/raw/Geolife Trajectories 1.3/Data/000/Trajectory/20081211044624.plt"
    )
    segments = segment_points(points)
    print(f"{len(points)} points -> {len(segments)} segment(s)")
    for s in segments:
        print(
            f"  segment: {len(s.points)} points, {s.points[0].timestamp} -> {s.points[-1].timestamp}"
        )
