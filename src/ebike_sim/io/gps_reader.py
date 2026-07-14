from __future__ import annotations

import csv
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

from ..models.gps_point import GpsPoint
from ..models.route_data import RouteData

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = ["lat", "lon", "ele", "time", "temperature"]


def _parse_timestamp(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError("Time stamps must end with Z for UTC")
    return datetime.fromisoformat(value[:-1].replace("Z", "")).replace(tzinfo=timezone.utc)


def read_gps_csv(path: str | Path) -> RouteData:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"GPS file not found: {csv_path}")
    if not csv_path.is_file():
        raise ValueError(f"GPS path is not a file: {csv_path}")

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        sample = handle.read(4096)
        if ";" not in sample:
            raise ValueError("GPS file must use semicolon as delimiter")
        handle.seek(0)
        reader = csv.DictReader(handle, delimiter=";")
        if reader.fieldnames is None:
            raise ValueError("GPS file is empty")
        missing = [column for column in EXPECTED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        points: list[GpsPoint] = []
        for row in reader:
            try:
                latitude = float(row["lat"])
                longitude = float(row["lon"])
                elevation_m = float(row["ele"])
                temperature_c = float(row["temperature"]) if row["temperature"] not in {"", None} else None
                timestamp = _parse_timestamp(row["time"])
            except (TypeError, ValueError) as exc:
                logger.warning("Skipping invalid GPS row: %s", row)
                continue

            if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
                logger.warning("Skipping GPS row with invalid coordinates: %s", row)
                continue
            if not (elevation_m == elevation_m and abs(elevation_m) != float("inf")):
                logger.warning("Skipping GPS row with invalid elevation: %s", row)
                continue
            if temperature_c is not None and not (temperature_c == temperature_c and abs(temperature_c) != float("inf")):
                logger.warning("Skipping GPS row with invalid temperature: %s", row)
                continue

            points.append(
                GpsPoint(
                    latitude=latitude,
                    longitude=longitude,
                    elevation_m=elevation_m,
                    timestamp=timestamp,
                    temperature_c=temperature_c,
                )
            )

    if len(points) < 2:
        raise ValueError("At least two valid GPS rows are required")

    points.sort(key=lambda point: point.timestamp)
    for previous, current in zip(points, points[1:]):
        if previous.timestamp == current.timestamp:
            logger.warning("Duplicate timestamp detected: %s", current.timestamp)

    return RouteData(points=points, segments=[], total_distance_m=0.0, total_duration_s=0.0, ascent_m=0.0, descent_m=0.0, average_speed_m_s=0.0, maximum_speed_m_s=0.0, maximum_power_w=0.0)
