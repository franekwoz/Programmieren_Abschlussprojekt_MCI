from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class GpsPoint:
    latitude: float
    longitude: float
    elevation_m: float
    timestamp: datetime
    temperature_c: float | None
