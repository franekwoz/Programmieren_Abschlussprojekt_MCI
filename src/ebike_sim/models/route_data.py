from __future__ import annotations

from dataclasses import dataclass

from .gps_point import GpsPoint
from .route_segment import RouteSegment


@dataclass
class RouteData:
    points: list[GpsPoint]
    segments: list[RouteSegment]
    total_distance_m: float
    total_duration_s: float
    ascent_m: float
    descent_m: float
    average_speed_m_s: float
    maximum_speed_m_s: float
    maximum_power_w: float
    total_breaking_energy_j: float = 0.0
