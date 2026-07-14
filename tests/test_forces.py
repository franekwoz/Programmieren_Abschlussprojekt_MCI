from datetime import datetime, timezone

import pytest

from src.ebike_sim.analysis.forces import calculate_forces
from src.ebike_sim.models.gps_point import GpsPoint
from src.ebike_sim.models.route_segment import RouteSegment


def test_negative_required_force_does_not_create_negative_propulsion():
    point = GpsPoint(latitude=47.0, longitude=12.0, elevation_m=0.0, timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc), temperature_c=20.0)
    segment = RouteSegment(
        start_point=point,
        end_point=point,
        duration_s=1.0,
        horizontal_distance_m=0.0,
        spatial_distance_m=0.0,
        elevation_difference_m=0.0,
        average_temperature_c=20.0,
        speed_m_s=0.0,
        acceleration_m_s2=-1.0,
        slope_ratio=0.0,
        slope_angle_rad=0.0,
        acceleration_force_n=0.0,
        grade_force_n=0.0,
        aerodynamic_force_n=0.0,
        required_force_n=0.0,
        propulsion_force_n=0.0,
        mechanical_power_w=0.0,
        wheel_torque_nm=0.0,
        motor_torque_nm=0.0,
        motor_current_a=0.0,
    )

    result = calculate_forces(
        segment,
        total_mass_kg=80.0,
        gravity_m_s2=9.81,
        air_density_kg_m3=1.225,
        cw_a_m2=0.5625,
        wheel_radius_m=0.35,
        gear_ratio=1.0,
        motor_constant_nm_per_a=1.5,
    )

    assert result.required_force_n < 0.0
    assert result.propulsion_force_n == 0.0
    assert result.mechanical_power_w == 0.0