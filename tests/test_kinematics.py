from datetime import datetime, timezone

import pytest

from src.ebike_sim.analysis.kinematics import (
    bidirectional_time_smoothing,
    calculate_route_data,
    exponential_smoothing_time_aware,
    haversine_distance_m,
)
from src.ebike_sim.models.gps_point import GpsPoint
from src.ebike_sim.models.route_data import RouteData


BASE_LAT = 47.0
BASE_LON = 12.0
BASE_TIME = datetime(2024, 1, 1, tzinfo=timezone.utc)
M_PER_DEG_LAT = 111_320.0


def make_point(index: int, seconds: float, elevation_m: float = 0.0) -> GpsPoint:
    return GpsPoint(
        latitude=BASE_LAT + (index * 10.0) / M_PER_DEG_LAT,
        longitude=BASE_LON,
        elevation_m=elevation_m,
        timestamp=BASE_TIME + __import__("datetime").timedelta(seconds=seconds),
        temperature_c=20.0,
    )


def make_route(points: list[GpsPoint]) -> RouteData:
    return RouteData(points=points, segments=[], total_distance_m=0.0, total_duration_s=0.0, ascent_m=0.0, descent_m=0.0, average_speed_m_s=0.0, maximum_speed_m_s=0.0, maximum_power_w=0.0)


def test_haversine_distance_is_reasonable():
    distance_m = haversine_distance_m(47.0, 12.0, 47.0, 12.0001)
    assert distance_m > 0.0


def test_constant_speed_produces_near_zero_acceleration():
    points = [make_point(index, seconds=index * 10.0) for index in range(5)]
    route = calculate_route_data(make_route(points))

    assert route.segments[0].acceleration_m_s2 == 0.0
    assert all(abs(segment.acceleration_m_s2) < 1e-3 for segment in route.segments)
    assert route.maximum_power_w < 1000.0


def test_short_interval_is_not_used_directly_for_smoothing():
    points = [
        make_point(0, 0.0),
        make_point(1, 10.0),
        make_point(20, 10.1),
        make_point(21, 20.1),
        make_point(22, 30.1),
    ]
    route = calculate_route_data(make_route(points))

    spike_segment = route.segments[1]
    assert spike_segment.raw_speed_m_s > 50.0
    assert spike_segment.speed_m_s < 10.0
    assert abs(spike_segment.acceleration_m_s2) < 5.0
    assert route.maximum_power_w < 2000.0


def test_large_gap_starts_new_group_with_zero_acceleration():
    points = [
        make_point(0, 0.0),
        make_point(1, 10.0),
        make_point(2, 20.0),
        make_point(3, 55.0),
        make_point(4, 65.0),
    ]
    route = calculate_route_data(make_route(points))

    assert route.segments[2].duration_s > 30.0
    assert route.segments[2].acceleration_m_s2 == 0.0


def test_single_speed_outlier_is_smoothed():
    points = [
        make_point(0, 0.0),
        make_point(1, 10.0),
        make_point(30, 20.0),
        make_point(31, 30.0),
        make_point(32, 40.0),
    ]
    route = calculate_route_data(make_route(points))

    outlier_segment = route.segments[1]
    neighbor_speed = route.segments[0].speed_m_s
    assert outlier_segment.raw_speed_m_s > 20.0
    assert abs(outlier_segment.speed_m_s - neighbor_speed) < abs(outlier_segment.raw_speed_m_s - neighbor_speed)


def test_time_aware_smoothing_uses_real_seconds():
    regular = bidirectional_time_smoothing([0.0, 1.0, 2.0], [1.0, 10.0, 1.0], 3.0)
    irregular = bidirectional_time_smoothing([0.0, 1.0, 20.0], [1.0, 10.0, 1.0], 3.0)

    assert regular != irregular


def test_average_speed_is_weighted_by_time():
    points = [make_point(index, seconds=index * 10.0) for index in range(4)]
    route = calculate_route_data(make_route(points))

    assert route.average_speed_m_s == pytest.approx(route.total_distance_m / route.total_duration_s)