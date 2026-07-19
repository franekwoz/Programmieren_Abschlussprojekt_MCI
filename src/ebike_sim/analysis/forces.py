from __future__ import annotations

import math

from ..extensions.braking_resistor import calculate_braking_resistor_power
from ..extensions.recuperation import calculate_recuperation_current
from ..extensions.rolling_resistance import calculate_rolling_resistance
from ..models.route_segment import RouteSegment

def calculate_forces(segment: RouteSegment, total_mass_kg: float, gravity_m_s2: float, air_density_kg_m3: float, cw_a_m2: float, wheel_radius_m: float, gear_ratio: float, motor_constant_nm_per_a: float, rolling_resistance_coefficient: float = 0.0, recuperation_efficiency: float = 0.0, maximum_recuperation_current_a: float = 0.0, nominal_battery_voltage_v: float = 37.0) -> RouteSegment:
    acceleration_force_n = total_mass_kg * segment.acceleration_m_s2
    grade_force_n = total_mass_kg * gravity_m_s2 * math.sin(segment.slope_angle_rad)
    aerodynamic_force_n = 0.5 * air_density_kg_m3 * cw_a_m2 * segment.speed_m_s**2
    rolling_resistance_force_n = calculate_rolling_resistance(total_mass_kg, gravity_m_s2, rolling_resistance_coefficient, segment.slope_angle_rad)    
    required_force_n = acceleration_force_n + grade_force_n + aerodynamic_force_n + rolling_resistance_force_n
    propulsion_force_n = max(required_force_n, 0.0)
    braking_force_n = max(-required_force_n, 0.0)
    braking_power_w = braking_force_n * segment.speed_m_s
    recuperation_current_a = 0.0
    rechargeable_power_w = 0.0
    if braking_power_w > 0.0 and recuperation_efficiency > 0.0 and maximum_recuperation_current_a > 0.0:
        recuperation_current_a = calculate_recuperation_current(
            braking_power_w,
            nominal_battery_voltage_v,
            recuperation_efficiency,
            maximum_recuperation_current_a,
        )
        rechargeable_power_w = recuperation_current_a * nominal_battery_voltage_v
    braking_resistor_power_w = calculate_braking_resistor_power(braking_power_w, rechargeable_power_w)
    mechanical_power_w = propulsion_force_n * segment.speed_m_s
    wheel_torque_nm = propulsion_force_n * wheel_radius_m
    motor_torque_nm = wheel_torque_nm / gear_ratio
    motor_current_a = motor_torque_nm / motor_constant_nm_per_a
    if recuperation_current_a > 0.0:
        motor_current_a = -recuperation_current_a

    segment.acceleration_force_n = acceleration_force_n if math.isfinite(acceleration_force_n) else 0.0
    segment.grade_force_n = grade_force_n if math.isfinite(grade_force_n) else 0.0
    segment.aerodynamic_force_n = aerodynamic_force_n if math.isfinite(aerodynamic_force_n) else 0.0
    segment.rolling_resistance_force_n = rolling_resistance_force_n if math.isfinite(rolling_resistance_force_n) else 0.0
    segment.required_force_n = required_force_n if math.isfinite(required_force_n) else 0.0
    segment.propulsion_force_n = propulsion_force_n if math.isfinite(propulsion_force_n) else 0.0
    segment.braking_resistor_power_w = braking_resistor_power_w if math.isfinite(braking_resistor_power_w) else 0.0
    segment.mechanical_power_w = mechanical_power_w if math.isfinite(mechanical_power_w) else 0.0
    segment.wheel_torque_nm = wheel_torque_nm if math.isfinite(wheel_torque_nm) else 0.0
    segment.motor_torque_nm = motor_torque_nm if math.isfinite(motor_torque_nm) else 0.0
    segment.motor_current_a = motor_current_a if math.isfinite(motor_current_a) else 0.0
    return segment
