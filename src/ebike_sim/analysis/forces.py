from __future__ import annotations

import math

from ..models.route_segment import RouteSegment


def calculate_forces(segment: RouteSegment, total_mass_kg: float, gravity_m_s2: float, air_density_kg_m3: float, cw_a_m2: float, wheel_radius_m: float, gear_ratio: float, motor_constant_nm_per_a: float) -> RouteSegment:
    acceleration_force_n = total_mass_kg * segment.acceleration_m_s2
    grade_force_n = total_mass_kg * gravity_m_s2 * math.sin(segment.slope_angle_rad)
    aerodynamic_force_n = 0.5 * air_density_kg_m3 * cw_a_m2 * segment.speed_m_s**2
    required_force_n = acceleration_force_n + grade_force_n + aerodynamic_force_n
    propulsion_force_n = max(required_force_n, 0.0)
    mechanical_power_w = propulsion_force_n * segment.speed_m_s
    wheel_torque_nm = propulsion_force_n * wheel_radius_m
    motor_torque_nm = wheel_torque_nm / gear_ratio
    motor_current_a = motor_torque_nm / motor_constant_nm_per_a

    segment.acceleration_force_n = acceleration_force_n if math.isfinite(acceleration_force_n) else 0.0
    segment.grade_force_n = grade_force_n if math.isfinite(grade_force_n) else 0.0
    segment.aerodynamic_force_n = aerodynamic_force_n if math.isfinite(aerodynamic_force_n) else 0.0
    segment.required_force_n = required_force_n if math.isfinite(required_force_n) else 0.0
    segment.propulsion_force_n = propulsion_force_n if math.isfinite(propulsion_force_n) else 0.0
    segment.mechanical_power_w = mechanical_power_w if math.isfinite(mechanical_power_w) else 0.0
    segment.wheel_torque_nm = wheel_torque_nm if math.isfinite(wheel_torque_nm) else 0.0
    segment.motor_torque_nm = motor_torque_nm if math.isfinite(motor_torque_nm) else 0.0
    segment.motor_current_a = motor_current_a if math.isfinite(motor_current_a) else 0.0
    return segment
