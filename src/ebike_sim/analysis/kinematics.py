from __future__ import annotations

import math
import logging
from dataclasses import dataclass
from statistics import median

from ..analysis.forces import calculate_forces
from ..extensions.air_density import calculate_air_density
from ..models.bike_parameters import BikeParameters
from ..models.gps_point import GpsPoint
from ..models.route_data import RouteData
from ..models.route_segment import RouteSegment

EARTH_RADIUS_M = 6_371_000.0
MIN_SPEED_INTERVAL_S = 0.5
MAX_CONTINUOUS_GAP_S = 30.0
MAX_REASONABLE_SPEED_M_S = 60.0 / 3.6
MEDIAN_WINDOW_S = 15.0
SMOOTHING_TIME_CONSTANT_S = 3.0

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SegmentKinematics:
    """Raw and smoothed kinematic values for a single GPS segment."""

    start_point: GpsPoint
    end_point: GpsPoint
    duration_s: float
    midpoint_time_s: float
    horizontal_distance_m: float
    spatial_distance_m: float
    elevation_difference_m: float
    average_temperature_c: float | None
    raw_speed_m_s: float
    raw_speed_is_valid: bool
    smoothed_speed_m_s: float = 0.0
    acceleration_m_s2: float = 0.0
    slope_ratio: float = 0.0
    slope_angle_rad: float = 0.0


def _is_finite(value: float) -> bool:
    return math.isfinite(value)


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def split_into_continuous_groups(segment_data: list[SegmentKinematics], max_gap_s: float) -> list[list[SegmentKinematics]]:
    """Split segments into continuous groups separated by large time gaps."""

    groups: list[list[SegmentKinematics]] = []
    current_group: list[SegmentKinematics] = []

    for segment in segment_data:
        if current_group and segment.duration_s > max_gap_s:
            groups.append(current_group)
            current_group = []
        current_group.append(segment)

    if current_group:
        groups.append(current_group)
    return groups


def rolling_time_median(times_s: list[float], values: list[float | None], window_s: float) -> list[float | None]:
    """Return a centered time-window median for valid values only."""

    half_window_s = window_s / 2.0
    result: list[float | None] = []

    for index, time_s in enumerate(times_s):
        value = values[index]
        if value is None or not _is_finite(value):
            result.append(None)
            continue

        window_values = [
            candidate
            for candidate_time, candidate in zip(times_s, values)
            if candidate is not None and _is_finite(candidate) and abs(candidate_time - time_s) <= half_window_s
        ]
        result.append(float(median(window_values)) if window_values else None)

    return result


def exponential_smoothing_time_aware(times_s: list[float], values: list[float], time_constant_s: float) -> list[float]:
    """Apply a time-aware one-direction exponential smoothing pass."""

    if not values:
        return []
    smoothed_values = [values[0]]
    previous_smoothed_value = values[0]

    for index in range(1, len(values)):
        delta_time_s = abs(times_s[index] - times_s[index - 1])
        alpha = 1.0 - math.exp(-delta_time_s / time_constant_s) if time_constant_s > 0.0 else 1.0
        previous_smoothed_value = previous_smoothed_value + alpha * (values[index] - previous_smoothed_value)
        smoothed_values.append(previous_smoothed_value)

    return smoothed_values


def bidirectional_time_smoothing(times_s: list[float], values: list[float], time_constant_s: float) -> list[float]:
    """Smooth values forward and backward and average both passes."""

    forward = exponential_smoothing_time_aware(times_s, values, time_constant_s)
    backward = list(reversed(exponential_smoothing_time_aware(list(reversed(times_s)), list(reversed(values)), time_constant_s)))
    return [(forward_value + backward_value) / 2.0 for forward_value, backward_value in zip(forward, backward)]


def interpolate_invalid_speeds(times_s: list[float], values: list[float | None]) -> list[float]:
    """Fill gaps within a continuous group using surrounding smoothed speeds."""

    valid_indices = [index for index, value in enumerate(values) if value is not None and _is_finite(value)]
    if not valid_indices:
        return [0.0 for _ in values]

    interpolated_values = [0.0 for _ in values]
    for index in valid_indices:
        interpolated_values[index] = float(values[index]) if values[index] is not None else 0.0

    for index, value in enumerate(values):
        if value is not None and _is_finite(value):
            continue

        left_candidates = [candidate_index for candidate_index in valid_indices if candidate_index < index]
        right_candidates = [candidate_index for candidate_index in valid_indices if candidate_index > index]

        left_index = left_candidates[-1] if left_candidates else None
        right_index = right_candidates[0] if right_candidates else None

        if left_index is not None and right_index is not None:
            left_time = times_s[left_index]
            right_time = times_s[right_index]
            if right_time > left_time:
                fraction = (times_s[index] - left_time) / (right_time - left_time)
                interpolated_values[index] = interpolated_values[left_index] + fraction * (interpolated_values[right_index] - interpolated_values[left_index])
                continue

        if left_index is not None:
            interpolated_values[index] = interpolated_values[left_index]
        elif right_index is not None:
            interpolated_values[index] = interpolated_values[right_index]

    return interpolated_values


def calculate_smoothed_acceleration(times_s: list[float], speeds_m_s: list[float]) -> list[float]:
    """Differentiate smoothed speeds with time-aware finite differences."""

    if not speeds_m_s:
        return []

    accelerations = [0.0 for _ in speeds_m_s]
    if len(speeds_m_s) == 1:
        return accelerations

    for index in range(1, len(speeds_m_s) - 1):
        delta_time_s = times_s[index + 1] - times_s[index - 1]
        if delta_time_s > 1e-9:
            accelerations[index] = (speeds_m_s[index + 1] - speeds_m_s[index - 1]) / delta_time_s
        else:
            accelerations[index] = 0.0

    delta_time_s = times_s[-1] - times_s[-2]
    accelerations[-1] = (speeds_m_s[-1] - speeds_m_s[-2]) / delta_time_s if delta_time_s > 1e-9 else 0.0
    return accelerations


def _estimate_force_terms(
    speed_m_s: float,
    acceleration_m_s2: float,
    slope_angle_rad: float,
    params: BikeParameters,
) -> tuple[float, float, float, float, float, float, float, float, float]:
    acceleration_force_n = params.total_mass_kg * acceleration_m_s2
    grade_force_n = params.total_mass_kg * params.gravity_m_s2 * math.sin(slope_angle_rad)
    aerodynamic_force_n = 0.5 * params.air_density_kg_m3 * params.cw_a_m2 * speed_m_s**2
    required_force_n = acceleration_force_n + grade_force_n + aerodynamic_force_n
    propulsion_force_n = max(required_force_n, 0.0)
    mechanical_power_w = propulsion_force_n * speed_m_s
    wheel_torque_nm = propulsion_force_n * params.wheel_radius_m
    motor_torque_nm = wheel_torque_nm / params.gear_ratio
    motor_current_a = motor_torque_nm / params.motor_constant_nm_per_a
    return (
        acceleration_force_n,
        grade_force_n,
        aerodynamic_force_n,
        required_force_n,
        propulsion_force_n,
        mechanical_power_w,
        wheel_torque_nm,
        motor_torque_nm,
        motor_current_a,
    )


def _build_segment_kinematics(points: list[GpsPoint]) -> tuple[list[SegmentKinematics], int, int, int, float, float]:
    raw_segments: list[SegmentKinematics] = []
    short_interval_count = 0
    gap_count = 0
    raw_max_speed_m_s = 0.0
    raw_max_acceleration_m_s2 = 0.0

    if not points:
        return raw_segments, short_interval_count, gap_count, 0, raw_max_speed_m_s, raw_max_acceleration_m_s2

    route_start_time = points[0].timestamp
    previous_raw_speed_m_s: float | None = None
    previous_midpoint_time_s: float | None = None

    for start_point, end_point in zip(points, points[1:]):
        duration_s = (end_point.timestamp - start_point.timestamp).total_seconds()
        if duration_s <= 0.0:
            continue

        if duration_s < MIN_SPEED_INTERVAL_S:
            short_interval_count += 1
        if duration_s > MAX_CONTINUOUS_GAP_S:
            gap_count += 1

        start_time_s = (start_point.timestamp - route_start_time).total_seconds()
        midpoint_time_s = start_time_s + duration_s / 2.0
        horizontal_distance_m = haversine_distance_m(start_point.latitude, start_point.longitude, end_point.latitude, end_point.longitude)
        elevation_difference_m = end_point.elevation_m - start_point.elevation_m
        spatial_distance_m = math.sqrt(horizontal_distance_m**2 + elevation_difference_m**2)
        raw_speed_m_s = spatial_distance_m / duration_s
        slope_ratio = elevation_difference_m / horizontal_distance_m if horizontal_distance_m > 0.0 else 0.0
        slope_angle_rad = math.atan2(elevation_difference_m, horizontal_distance_m) if horizontal_distance_m > 0.0 else 0.0

        average_temperature_c: float | None
        temperatures = [value for value in (start_point.temperature_c, end_point.temperature_c) if value is not None]
        if temperatures:
            average_temperature_c = sum(temperatures) / len(temperatures)
        else:
            average_temperature_c = None

        raw_speed_is_valid = duration_s >= MIN_SPEED_INTERVAL_S and _is_finite(raw_speed_m_s) and raw_speed_m_s <= MAX_REASONABLE_SPEED_M_S
        raw_segments.append(
            SegmentKinematics(
                start_point=start_point,
                end_point=end_point,
                duration_s=duration_s,
                midpoint_time_s=midpoint_time_s,
                horizontal_distance_m=horizontal_distance_m,
                spatial_distance_m=spatial_distance_m,
                elevation_difference_m=elevation_difference_m,
                average_temperature_c=average_temperature_c,
                raw_speed_m_s=raw_speed_m_s,
                raw_speed_is_valid=raw_speed_is_valid,
                slope_ratio=slope_ratio,
                slope_angle_rad=slope_angle_rad,
            )
        )

        if raw_speed_m_s > raw_max_speed_m_s:
            raw_max_speed_m_s = raw_speed_m_s

        if previous_raw_speed_m_s is not None and previous_midpoint_time_s is not None:
            delta_time_s = midpoint_time_s - previous_midpoint_time_s
            if delta_time_s > 1e-9:
                raw_acceleration_m_s2 = (raw_speed_m_s - previous_raw_speed_m_s) / delta_time_s
                raw_max_acceleration_m_s2 = max(raw_max_acceleration_m_s2, abs(raw_acceleration_m_s2))
        previous_raw_speed_m_s = raw_speed_m_s
        previous_midpoint_time_s = midpoint_time_s

    return raw_segments, short_interval_count, gap_count, len(raw_segments), raw_max_speed_m_s, raw_max_acceleration_m_s2


def _smooth_group(group: list[SegmentKinematics]) -> None:
    if not group:
        return

    times_s = [segment.midpoint_time_s for segment in group]
    support_values: list[float | None] = [segment.raw_speed_m_s if segment.raw_speed_is_valid else None for segment in group]
    median_values = rolling_time_median(times_s, support_values, MEDIAN_WINDOW_S)
    support_indices = [index for index, segment in enumerate(group) if segment.raw_speed_is_valid and median_values[index] is not None]

    if support_indices:
        support_times = [times_s[index] for index in support_indices]
        support_median_values = [float(median_values[index]) for index in support_indices if median_values[index] is not None]
        smoothed_support = bidirectional_time_smoothing(support_times, support_median_values, SMOOTHING_TIME_CONSTANT_S)
        smoothed_values: list[float | None] = [None for _ in group]
        for support_index, smoothed_speed_m_s in zip(support_indices, smoothed_support):
            smoothed_values[support_index] = smoothed_speed_m_s
        final_speeds = interpolate_invalid_speeds(times_s, smoothed_values)
    else:
        final_speeds = [0.0 for _ in group]

    accelerations = calculate_smoothed_acceleration(times_s, final_speeds)
    for segment, smoothed_speed_m_s, acceleration_m_s2 in zip(group, final_speeds, accelerations):
        segment.smoothed_speed_m_s = smoothed_speed_m_s
        segment.acceleration_m_s2 = acceleration_m_s2


def calculate_route_data(route_data: RouteData, params: BikeParameters | None = None) -> RouteData:
    points = route_data.points
    params = params or BikeParameters()
    raw_segments, short_interval_count, gap_count, raw_segment_count, raw_max_speed_m_s, raw_max_acceleration_m_s2 = _build_segment_kinematics(points)
    groups = split_into_continuous_groups(raw_segments, MAX_CONTINUOUS_GAP_S)

    for group in groups:
        _smooth_group(group)

    segments: list[RouteSegment] = []
    total_distance_m = 0.0
    total_duration_s = 0.0
    ascent_m = 0.0
    descent_m = 0.0
    maximum_smoothed_speed_m_s = 0.0
    maximum_smoothed_acceleration_m_s2 = 0.0
    maximum_power_w = 0.0
    total_breaking_energy_j = 0.0

    for group in groups:
        for segment_kinematics in group:
            segment = RouteSegment(
                start_point=segment_kinematics.start_point,
                end_point=segment_kinematics.end_point,
                duration_s=segment_kinematics.duration_s,
                horizontal_distance_m=segment_kinematics.horizontal_distance_m,
                spatial_distance_m=segment_kinematics.spatial_distance_m,
                elevation_difference_m=segment_kinematics.elevation_difference_m,
                average_temperature_c=segment_kinematics.average_temperature_c,
                speed_m_s=segment_kinematics.smoothed_speed_m_s,
                acceleration_m_s2=segment_kinematics.acceleration_m_s2,
                slope_ratio=segment_kinematics.slope_ratio,
                slope_angle_rad=segment_kinematics.slope_angle_rad,
                acceleration_force_n=0.0,
                grade_force_n=0.0,
                aerodynamic_force_n=0.0,
                required_force_n=0.0,
                propulsion_force_n=0.0,
                mechanical_power_w=0.0,
                wheel_torque_nm=0.0,
                motor_torque_nm=0.0,
                motor_current_a=0.0,
                raw_speed_m_s=segment_kinematics.raw_speed_m_s,
            )
            segment_air_density_kg_m3 = params.air_density_kg_m3
            if segment_kinematics.average_temperature_c is not None:
                average_elevation_m = (segment_kinematics.start_point.elevation_m + segment_kinematics.end_point.elevation_m) / 2.0
                try:
                    segment_air_density_kg_m3 = calculate_air_density(average_elevation_m, segment_kinematics.average_temperature_c)
                except ValueError:
                    logger.warning("Falling back to default air density for an invalid elevation/temperature reading.")

            segment = calculate_forces(
                segment,
                total_mass_kg=params.total_mass_kg,
                gravity_m_s2=params.gravity_m_s2,
                air_density_kg_m3=segment_air_density_kg_m3,
                cw_a_m2=params.cw_a_m2,
                wheel_radius_m=params.wheel_radius_m,
                gear_ratio=params.gear_ratio,
                motor_constant_nm_per_a=params.motor_constant_nm_per_a,
                rolling_resistance_coefficient=params.rolling_resistance_coefficient,
                recuperation_efficiency=params.recuperation_efficiency,
                maximum_recuperation_current_a=params.maximum_recuperation_current_a,
                nominal_battery_voltage_v=params.nominal_battery_voltage_v,
            )

            segments.append(segment)
            total_distance_m += segment.horizontal_distance_m
            total_duration_s += segment.duration_s
            if segment.elevation_difference_m > 0.0:
                ascent_m += segment.elevation_difference_m
            elif segment.elevation_difference_m < 0.0:
                descent_m += -segment.elevation_difference_m
            maximum_smoothed_speed_m_s = max(maximum_smoothed_speed_m_s, segment.speed_m_s)
            maximum_smoothed_acceleration_m_s2 = max(maximum_smoothed_acceleration_m_s2, abs(segment.acceleration_m_s2))
            maximum_power_w = max(maximum_power_w, segment.mechanical_power_w)
            total_braking_energy_j += segment.braking_resistor_power_w * segment.duration_s

    route_data.segments = segments
    route_data.total_distance_m = total_distance_m
    route_data.total_duration_s = total_duration_s
    route_data.ascent_m = ascent_m
    route_data.descent_m = descent_m
    route_data.average_speed_m_s = total_distance_m / total_duration_s if total_duration_s > 0.0 else 0.0
    route_data.maximum_speed_m_s = maximum_smoothed_speed_m_s
    route_data.maximum_power_w = maximum_power_w
    route_data.total_breaking_energy_j = total_braking_energy_j

    logger.info(
        "Kinematics: raw_segments=%d short_intervals=%d gap_intervals=%d max_raw_speed=%.3f m/s max_smoothed_speed=%.3f m/s max_raw_accel=%.3f m/s^2 max_smoothed_accel=%.3f m/s^2 max_power=%.3f W",
        raw_segment_count,
        short_interval_count,
        gap_count,
        raw_max_speed_m_s,
        maximum_smoothed_speed_m_s,
        raw_max_acceleration_m_s2,
        maximum_smoothed_acceleration_m_s2,
        maximum_power_w,
    )
    return route_data
