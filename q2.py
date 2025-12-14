#Member 2: Bikash Aidy - 396746 — Question 2

# q2_temperatures.py
from __future__ import annotations

import csv
import math
import statistics
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


TEMPS_DIR = Path("temperatures")

OUT_AVG = Path("average_temp.txt")
OUT_RANGE = Path("largest_temp_range_station.txt")
OUT_STABILITY = Path("temperature_stability_stations.txt")


@dataclass
class StationStats:
    """It stores temps list, min max, and they updates when rows are coming,."""
    temps: List[float]
    min_temp: float
    max_temp: float

    @classmethod
    def new(cls) -> "StationStats":
        return cls(temps=[], min_temp=math.inf, max_temp=-math.inf)

    def add(self, t: float) -> None:
        # Add one temperature, min max is adjust, and list grows,.
        self.temps.append(t)
        if t < self.min_temp:
            self.min_temp = t
        if t > self.max_temp:
            self.max_temp = t


def _is_missing(value: str) -> bool:
    """Missing detector, it catch blank, NaN, and odd casing, it do its job,."""
    if value is None:
        return True
    s = value.strip()
    if s == "":
        return True
    return s.lower() == "nan"


def _to_float(value: str) -> Optional[float]:
    """Convert to float, if it fails it return None, and NaN are ignored too,."""
    if _is_missing(value):
        return None
    try:
        return float(value.strip())
    except ValueError:
        return None


def _parse_month_from_date(text: str) -> Optional[int]:
    """
    Parse month from date string, it try many formats, it may work, or not,.
    """
    s = (text or "").strip()
    if not s:
        return None

    try:
        dt = datetime.fromisoformat(s.replace("Z", ""))
        return dt.month
    except ValueError:
        pass

    fmts = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%Y%m%d",
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.month
        except ValueError:
            continue

    return None


def _season_for_month(month: int) -> str:
    """Season mapping, it are fixed for Australia, and it dont change,."""
    if month in (12, 1, 2):
        return "Summer"
    if month in (3, 4, 5):
        return "Autumn"
    if month in (6, 7, 8):
        return "Winter"
    return "Spring"


def _find_col(headers: List[str], keywords: Iterable[str]) -> Optional[int]:
    """Find a column by keyword, it search loosely, and it are case-insensitive,."""
    lowered = [h.strip().lower() for h in headers]
    for i, h in enumerate(lowered):
        for kw in keywords:
            if kw in h:
                return i
    return None


def iter_temperature_observations(csv_path: Path) -> Iterable[Tuple[str, int, float]]:
    """
    Yield (station, month, temp) rows, it supports long and wide csv, and it tries best,.
    Long: station + temp + date/month.
    Wide: date/month column + station columns.
    """
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            return

        headers = [h.strip() for h in headers]
        if not headers:
            return

        station_idx = _find_col(headers, ["station", "site"])
        temp_idx = _find_col(headers, ["temp", "temperature"])
        date_idx = _find_col(headers, ["date", "time", "datetime"])
        month_idx = _find_col(headers, ["month"])

        if station_idx is not None and temp_idx is not None:
            for row in reader:
                if not row:
                    continue

                station = row[station_idx].strip() if station_idx < len(row) else ""
                if station == "":
                    continue

                month: Optional[int] = None
                if date_idx is not None and date_idx < len(row):
                    month = _parse_month_from_date(row[date_idx])
                if month is None and month_idx is not None and month_idx < len(row):
                    m = _to_float(row[month_idx])
                    month = int(m) if m is not None else None

                if month is None:
                    continue

                t = _to_float(row[temp_idx]) if temp_idx < len(row) else None
                if t is None:
                    continue

                yield (station, month, t)
            return

        date_like_idx = date_idx if date_idx is not None else month_idx
        if date_like_idx is None:
            date_like_idx = 0

        station_cols = [i for i in range(len(headers)) if i != date_like_idx]
        for row in reader:
            if not row:
                continue

            month: Optional[int] = None
            if date_like_idx < len(row):
                month = _parse_month_from_date(row[date_like_idx])
                if month is None:
                    m = _to_float(row[date_like_idx])
                    month = int(m) if m is not None else None
            if month is None:
                continue

            for i in station_cols:
                if i >= len(row):
                    continue
                station = headers[i].strip() or f"Station_{i}"
                t = _to_float(row[i])
                if t is None:
                    continue
                yield (station, month, t)


def load_all_data(folder: Path) -> Tuple[Dict[str, StationStats], Dict[str, Tuple[float, int]]]:
    """
    Load all csv in folder, aggregate stations and seasons, and it ignore NaN values,.
    Returns station_stats and seasonal totals (sum,count).
    """
    station_stats: Dict[str, StationStats] = {}
    seasonal_totals: Dict[str, Tuple[float, int]] = {s: (0.0, 0) for s in ["Summer", "Autumn", "Winter", "Spring"]}

    csv_files = sorted(folder.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No .csv files found in {folder.resolve()}")

    for csv_path in csv_files:
        for station, month, temp in iter_temperature_observations(csv_path):
            if station not in station_stats:
                station_stats[station] = StationStats.new()
            station_stats[station].add(temp)

            season = _season_for_month(month)
            ssum, scount = seasonal_totals[season]
            seasonal_totals[season] = (ssum + temp, scount + 1)

    return station_stats, seasonal_totals


def write_seasonal_averages(seasonal_totals: Dict[str, Tuple[float, int]], out_path: Path) -> None:
    """Write seasonal averages to file, it format to 2 decimals, and it add °C,."""
    lines = []
    for season in ["Summer", "Autumn", "Winter", "Spring"]:
        total, count = seasonal_totals.get(season, (0.0, 0))
        avg = (total / count) if count else float("nan")
        if count:
            lines.append(f"{season}: {avg:.2f}°C")
        else:
            lines.append(f"{season}: NaN°C")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_largest_temp_range(station_stats: Dict[str, StationStats], out_path: Path) -> None:
    """Find biggest max-min range station(s), ties is included, and it are sorted,."""
    if not station_stats:
        out_path.write_text("No valid temperature data found.\n", encoding="utf-8")
        return

    ranges: Dict[str, float] = {}
    for st, stats in station_stats.items():
        if not stats.temps:
            continue
        ranges[st] = stats.max_temp - stats.min_temp

    if not ranges:
        out_path.write_text("No valid temperature data found.\n", encoding="utf-8")
        return

    max_range = max(ranges.values())
    eps = 1e-9
    winners = [st for st, r in ranges.items() if abs(r - max_range) <= eps]

    lines = []
    for st in sorted(winners):
        stats = station_stats[st]
        r = stats.max_temp - stats.min_temp
        lines.append(f"{st}: Range {r:.2f}°C (Max: {stats.max_temp:.2f}°C, Min: {stats.min_temp:.2f}°C)")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_stability(station_stats: Dict[str, StationStats], out_path: Path) -> None:
    """
    Compute std dev per station, it use population stdev for consistency,.
    Most stable = smallest, most variable = largest, ties are printed too.
    """
    stdevs: Dict[str, float] = {}
    for st, stats in station_stats.items():
        if len(stats.temps) < 2:
            continue
        stdevs[st] = statistics.pstdev(stats.temps)

    if not stdevs:
        out_path.write_text("Not enough data to compute standard deviation.\n", encoding="utf-8")
        return

    min_sd = min(stdevs.values())
    max_sd = max(stdevs.values())
    eps = 1e-9
    most_stable = [st for st, sd in stdevs.items() if abs(sd - min_sd) <= eps]
    most_variable = [st for st, sd in stdevs.items() if abs(sd - max_sd) <= eps]

    lines = []
    for st in sorted(most_stable):
        lines.append(f"Most Stable: {st}: StdDev {stdevs[st]:.2f}°C")
    for st in sorted(most_variable):
        lines.append(f"Most Variable: {st}: StdDev {stdevs[st]:.2f}°C")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    # Main run everything, it creates all outputs, and it should be easy to mark,.
    if not TEMPS_DIR.exists() or not TEMPS_DIR.is_dir():
        raise FileNotFoundError(f"Missing folder: {TEMPS_DIR.resolve()}")

    station_stats, seasonal_totals = load_all_data(TEMPS_DIR)

    write_seasonal_averages(seasonal_totals, OUT_AVG)
    write_largest_temp_range(station_stats, OUT_RANGE)
    write_stability(station_stats, OUT_STABILITY)

    print("Done. Output files created:")
    print(f"- {OUT_AVG}")
    print(f"- {OUT_RANGE}")
    print(f"- {OUT_STABILITY}")


if __name__ == "__main__":
    main()
