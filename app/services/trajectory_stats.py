from datetime import datetime

from geoalchemy2.functions import ST_Intersects, ST_MakeEnvelope
from sqlalchemy import Time, cast, func
from sqlalchemy.orm import Session

from app.db.models import Trajectory


def stats_by_mode(db: Session, mode: str | None = None) -> list[dict]:
    """Average speed/distance/duration, grouped by mode (or for one mode).

    Returns one row per mode: {mode, trip_count, avg_speed_mps, avg_distance_m, avg_duration_s}.
    Trajectories with mode=None are excluded, since grouping by an unknown
    mode isn't meaningful for this query.
    """
    query = (
        db.query(
            Trajectory.mode,
            func.count(Trajectory.id).label("trip_count"),
            func.avg(Trajectory.avg_speed_mps).label("avg_speed_mps"),
            func.avg(Trajectory.distance_m).label("avg_distance_m"),
            func.avg(Trajectory.duration_s).label("avg_duration_s"),
        )
        .filter(Trajectory.mode.isnot(None))
        .group_by(Trajectory.mode)
    )
    if mode is not None:
        query = query.filter(Trajectory.mode == mode)

    return [
        {
            "mode": row.mode,
            "trip_count": row.trip_count,
            "avg_speed_mps": float(row.avg_speed_mps),
            "avg_distance_m": float(row.avg_distance_m),
            "avg_duration_s": float(row.avg_duration_s),
        }
        for row in query.all()
    ]


def trip_count_in_time_range(
    db: Session, start_hour: int, end_hour: int, mode: str | None = None
) -> int:
    """Count trajectories whose start_time falls within [start_hour, end_hour)
    of the day, regardless of the date (e.g. "all trips starting between 8am
    and 9am"). Hours are in 24h format, 0-23.
    """
    query = db.query(func.count(Trajectory.id)).filter(
        cast(Trajectory.start_time, Time) >= f"{start_hour:02d}:00:00",
        cast(Trajectory.start_time, Time) < f"{end_hour:02d}:00:00",
    )
    if mode is not None:
        query = query.filter(Trajectory.mode == mode)

    return query.scalar()


def trips_in_bounding_box(
    db: Session,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    mode: str | None = None,
) -> list[dict]:
    """Trajectories whose path intersects a given lat/lon bounding box.

    Returns {trajectory_id, mode, distance_m, avg_speed_mps} per matching trip.
    A simple rectangular bounding box is enough for an MVP "trips in this
    area" query; a polygon-based ST_Intersects could replace this later if
    a non-rectangular area is needed.
    """
    envelope = ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
    query = db.query(Trajectory).filter(ST_Intersects(Trajectory.geom, envelope))
    if mode is not None:
        query = query.filter(Trajectory.mode == mode)

    return [
        {
            "trajectory_id": t.id,
            "mode": t.mode,
            "distance_m": t.distance_m,
            "avg_speed_mps": t.avg_speed_mps,
        }
        for t in query.all()
    ]
