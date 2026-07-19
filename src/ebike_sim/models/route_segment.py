from __future__ import annotations

from dataclasses import dataclass

from .gps_point import GpsPoint


@dataclass
class RouteSegment:
    start_point: GpsPoint
    end_point: GpsPoint
    duration_s: float
    horizontal_distance_m: float
    spatial_distance_m: float
    elevation_difference_m: float
    average_temperature_c: float | None
    speed_m_s: float
    acceleration_m_s2: float
    slope_ratio: float
    slope_angle_rad: float
    acceleration_force_n: float
    grade_force_n: float
    aerodynamic_force_n: float
    required_force_n: float
    propulsion_force_n: float
    mechanical_power_w: float
    wheel_torque_nm: float
    motor_torque_nm: float
    motor_current_a: float
    raw_speed_m_s: float = 0.0
    rolling_resistance_force_n: float = 0.0
    braking_resistance_power_w: float = 0.0
