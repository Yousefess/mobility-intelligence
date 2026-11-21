from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class RawPoint:
    lat: float
    lon: float
    altitude_m: float | None
    timestamp: datetime


def parse_plt_file(path: str) -> list[RawPoint]:
    """Parse a single GeoLife .plt file into a list of RawPoint.

    File format (after a fixed 6-line header):
    lat,lon,0,altitude_ft,days_since_epoch,date,time
    """
    points: list[RawPoint] = []
    with open(path, "r") as f:
        lines = f.readlines()[6:]  # skip the 6-line header

    for line in lines:
        parts = line.strip().split(",")
        if len(parts) < 7:
            continue
        lat = float(parts[0])
        lon = float(parts[1])
        altitude_ft = float(parts[3])
        altitude_m = (
            altitude_ft * 0.3048 if altitude_ft != -777 else None
        )  # -777 = invalid in GeoLife
        date_str = parts[5]
        time_str = parts[6]
        ts = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        points.append(RawPoint(lat=lat, lon=lon, altitude_m=altitude_m, timestamp=ts))

    return points


# if __name__ == "__main__":
#     points = parse_plt_file(
#         "data/raw/Geolife Trajectories 1.3/Data/000/Trajectory/20081211044624.plt"
#     )
#     print(len(points))
#     print(points[0])
#     print(points[-1])
