from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SimulationResult:
    battery_type: str
    current_profile: list[float]
    duration_profile: list[float]
    time_profile: list[float]
    voltage_profile: list[float]
    soc_profile: list[float]
    distance_profile: list[float]
    speed_profile: list[float]
    power_profile: list[float]
    elevation_profile: list[float]
    temperature_profile: list[float | None]
