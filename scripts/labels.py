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


def match_mode(
    start: datetime, end: datetime, intervals: list[LabelInterval]
) -> str | None:
    """Return the mode of the label interval that this trajectory's time
    range falls inside (or overlaps most with). Returns None if no label
    file exists for this user, or no interval covers this time range.
    """
    for interval in intervals:
        if start >= interval.start_time and end <= interval.end_time:
            return interval.mode
    return None
