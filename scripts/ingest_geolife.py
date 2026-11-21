"""
Ingest GeoLife trajectories into the database.

Usage:
    python3 -m scripts.ingest_geolife

Only processes users that have a labels.txt file (the 69 labeled users),
as agreed: real transport mode, clean data, extendable later to all 182.
"""

import os

from geoalchemy2.elements import WKTElement

from app.db.session import SessionLocal
from app.db.models import User, Trajectory, TrajectoryPoint
from scripts.geolife_parser import parse_plt_file
from scripts.segment import segment_points
from scripts.stats import compute_stats
from scripts.labels import parse_labels_file, match_mode

DATA_ROOT = "data/raw/Geolife Trajectories 1.3/Data"


def points_to_linestring(points) -> WKTElement:
    coords = ", ".join(f"{p.lon} {p.lat}" for p in points)
    return WKTElement(f"LINESTRING({coords})", srid=4326)


def point_to_point_geom(p) -> WKTElement:
    return WKTElement(f"POINT({p.lon} {p.lat})", srid=4326)


def get_labeled_user_ids(data_root: str) -> list[str]:
    user_ids = []
    for entry in sorted(os.listdir(data_root)):
        labels_path = os.path.join(data_root, entry, "labels.txt")
        if os.path.isfile(labels_path):
            user_ids.append(entry)
    return user_ids


def ingest_user(db, geolife_id: str) -> None:
    user_dir = os.path.join(DATA_ROOT, geolife_id)
    traj_dir = os.path.join(user_dir, "Trajectory")
    labels_path = os.path.join(user_dir, "labels.txt")

    # resumable: skip users already ingested
    existing = db.query(User).filter_by(geolife_id=geolife_id).first()
    if existing is not None:
        print(f"  user {geolife_id}: already ingested, skipping")
        return

    label_intervals = parse_labels_file(labels_path)

    user = User(geolife_id=geolife_id)
    db.add(user)
    db.flush()  # get user.id without committing yet

    plt_files = sorted(f for f in os.listdir(traj_dir) if f.endswith(".plt"))
    trajectory_count = 0

    for plt_file in plt_files:
        plt_path = os.path.join(traj_dir, plt_file)
        raw_points = parse_plt_file(plt_path)
        segments = segment_points(raw_points)

        for segment in segments:
            pts = segment.points
            stats = compute_stats(pts)
            mode = match_mode(pts[0].timestamp, pts[-1].timestamp, label_intervals)

            trajectory = Trajectory(
                user_id=user.id,
                mode=mode,
                start_time=pts[0].timestamp,
                end_time=pts[-1].timestamp,
                distance_m=stats.distance_m,
                duration_s=stats.duration_s,
                avg_speed_mps=stats.avg_speed_mps,
                geom=points_to_linestring(pts),
            )
            db.add(trajectory)
            db.flush()  # get trajectory.id

            POINT_CHUNK_SIZE = 200
            point_objs = [
                TrajectoryPoint(
                    trajectory_id=trajectory.id,
                    seq=seq,
                    timestamp=p.timestamp,
                    altitude_m=p.altitude_m,
                    geom=point_to_point_geom(p),
                )
                for seq, p in enumerate(pts)
            ]
            for i in range(0, len(point_objs), POINT_CHUNK_SIZE):
                chunk = point_objs[i : i + POINT_CHUNK_SIZE]
                db.add_all(chunk)
                db.flush()  # push this chunk now, instead of one giant statement at the end

            trajectory_count += 1

    db.commit()
    print(
        f"  user {geolife_id}: {len(plt_files)} files -> {trajectory_count} trajectories"
    )


def main():
    user_ids = get_labeled_user_ids(DATA_ROOT)
    print(f"Found {len(user_ids)} labeled users")

    db = SessionLocal()
    try:
        for geolife_id in user_ids:
            ingest_user(db, geolife_id)
    finally:
        db.close()


if __name__ == "__main__":
    main()
