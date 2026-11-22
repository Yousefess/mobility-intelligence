from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class LabelInterval:
    start_time: datetime
    end_time: datetime
    mode: str


def parse_labels_file(path: str) -> list[LabelInterval]:
    """Parse a GeoLife labels.txt file.

    Format (tab-separated, header line first):
    Start Time<TAB>End Time<TAB>Transportation Mode
    2008/10/23 11:17:33<TAB>2008/10/23 11:35:28<TAB>bus
    """
    intervals: list[LabelInterval] = []
    with open(path, "r") as f:
        lines = f.readlines()[1:]  # skip header

    for line in lines:
        parts = line.strip().split("\t")
        if len(parts) != 3:
            continue
        start = datetime.strptime(parts[0], "%Y/%m/%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        end = datetime.strptime(parts[1], "%Y/%m/%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        mode = parts[2]
        intervals.append(LabelInterval(start_time=start, end_time=end, mode=mode))

    return intervals


MIN_OVERLAP_RATIO = 0.5


def match_mode(
    start: datetime, end: datetime, intervals: list[LabelInterval]
) -> str | None:
    """Return the mode of the label interval that overlaps most with this
    trajectory's time range, as long as that overlap covers at least
    MIN_OVERLAP_RATIO of the trajectory's own duration.

    This replaces strict containment (trajectory fully inside one labeled
    interval), which left most trajectories unlabeled because segmentation
    boundaries (file splits, gap threshold) rarely line up exactly with
    GeoLife's label interval boundaries.
    """
    traj_duration = (end - start).total_seconds()
    if traj_duration <= 0:
        return None

    best_mode: str | None = None
    best_overlap = 0.0

    for interval in intervals:
        overlap_start = max(start, interval.start_time)
        overlap_end = min(end, interval.end_time)
        overlap = (overlap_end - overlap_start).total_seconds()
        if overlap > best_overlap:
            best_overlap = overlap
            best_mode = interval.mode

    if best_overlap / traj_duration >= MIN_OVERLAP_RATIO:
        return best_mode
    return None
