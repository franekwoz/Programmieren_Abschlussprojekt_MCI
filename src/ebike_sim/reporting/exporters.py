from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ..models.battery import BatteryPack
from ..models.route_data import RouteData
from ..simulation.battery_simulator import BatterySimulator


def export_summary(route_data: RouteData, simulator: BatterySimulator, battery: BatteryPack, output_dir: str | Path) -> dict[str, object]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    compass_direction_counts = Counter(segment.compass_direction for segment in route_data.segments)
    dominant_compass_direction = compass_direction_counts.most_common(1)[0][0] if compass_direction_counts else None
    summary = {
        "battery_type": battery.battery_type,
        "gps_points": len(route_data.points),
        "valid_segments": len(route_data.segments),
        "total_distance_m": round(route_data.total_distance_m, 3),
        "total_duration_s": round(route_data.total_duration_s, 3),
        "average_speed_m_s": round(route_data.average_speed_m_s, 3),
        "maximum_speed_m_s": round(route_data.maximum_speed_m_s, 3),
        "ascent_m": round(route_data.ascent_m, 3),
        "descent_m": round(route_data.descent_m, 3),
        "dominant_compass_direction": dominant_compass_direction,
        "compass_direction_distribution": dict(compass_direction_counts),
        "maximum_power_w": round(route_data.maximum_power_w, 3),
        "total_braking_energy_j": round(route_data.total_braking_energy_j / 3600.0, 3),
        "rejected_recuperation_energy_wh": round(
            sum(
                power_w * duration_s
                for power_w, duration_s in zip(simulator.rejected_recuperation_power_w, simulator.duration_profile)
            )
            / 3600.0,
            3,
        ),
        "maximum_motor_current_a": round(max((segment.motor_current_a for segment in route_data.segments), default=0.0), 3),
        "initial_soc": round(battery.initial_soc, 3),
        "final_soc": round(battery.soc, 3),
        "minimum_voltage_v": round(min(simulator.voltage_profile), 3) if simulator.voltage_profile else 0.0,
        "average_temperature_c": round(sum(point.temperature_c for point in route_data.points if point.temperature_c is not None) / len([point for point in route_data.points if point.temperature_c is not None]), 3) if any(point.temperature_c is not None for point in route_data.points) else None,
        "minimum_temperature_c": round(min(point.temperature_c for point in route_data.points if point.temperature_c is not None), 3) if any(point.temperature_c is not None for point in route_data.points) else None,
        "maximum_temperature_c": round(max(point.temperature_c for point in route_data.points if point.temperature_c is not None), 3) if any(point.temperature_c is not None for point in route_data.points) else None,
        "empty": battery.is_empty(),
    }

    (output_path / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_path / "summary.txt").write_text("\n".join(f"{key}: {value}" for key, value in summary.items()), encoding="utf-8")
    return summary
