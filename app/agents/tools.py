from langchain_core.tools import tool

from app.db.session import SessionLocal
from app.services import trajectory_stats


@tool
def get_stats_by_mode(mode: str | None = None) -> list[dict]:
    """Get average speed (m/s), distance (m), and duration (s) of trips,
    grouped by transport mode (walk, bike, bus, car, taxi, subway, train,
    airplane, run, boat). Pass a specific mode to filter to just that one,
    or omit it to get stats for every mode.
    """
    db = SessionLocal()
    try:
        return trajectory_stats.stats_by_mode(db, mode=mode)
    finally:
        db.close()


@tool
def get_trip_count_in_time_range(
    start_hour: int, end_hour: int, mode: str | None = None
) -> int:
    """Count trips that started between start_hour and end_hour (24h format,
    0-23), regardless of the date. For example, start_hour=8, end_hour=9
    counts trips starting anytime between 8:00am and 8:59am across all days.
    Optionally filter by transport mode.
    """
    db = SessionLocal()
    try:
        return trajectory_stats.trip_count_in_time_range(
            db, start_hour=start_hour, end_hour=end_hour, mode=mode
        )
    finally:
        db.close()


@tool
def get_trips_in_bounding_box(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    mode: str | None = None,
) -> dict:
    """Find trips whose path passes through a rectangular geographic area,
    given as a bounding box of longitude/latitude corners. Returns the
    matching trip count and a short sample of trip details. Optionally
    filter by transport mode.
    """
    db = SessionLocal()
    try:
        trips = trajectory_stats.trips_in_bounding_box(
            db,
            min_lon=min_lon,
            min_lat=min_lat,
            max_lon=max_lon,
            max_lat=max_lat,
            mode=mode,
        )
        return {"trip_count": len(trips), "sample": trips[:5]}
    finally:
        db.close()


ALL_TOOLS = [get_stats_by_mode, get_trip_count_in_time_range, get_trips_in_bounding_box]
