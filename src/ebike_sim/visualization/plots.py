from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ..analysis.kinematics import calculate_route_data
from ..models.route_data import RouteData
from ..simulation.battery_simulator import BatterySimulator


def _save_or_show(fig, path: Path | None = None) -> None:
    if path is not None:
        fig.savefig(path, dpi=150, bbox_inches="tight")
    else:
        plt.close(fig)


def create_all_plots(route_data: RouteData, simulator: BatterySimulator, output_dir: str | Path) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    speed_values = [segment.speed_m_s for segment in route_data.segments]
    power_values = [segment.mechanical_power_w for segment in route_data.segments]
    times = [0.0] + [sum(seg.duration_s for seg in route_data.segments[:i]) for i in range(1, len(route_data.segments) + 1)]

    fig, ax = plt.subplots()
    ax.plot(times, speed_values + [speed_values[-1]] if speed_values else [0.0], label="speed")
    ax.set_xlabel("Time / s")
    ax.set_ylabel("Speed / m/s")
    ax.grid(True)
    fig.tight_layout()
    _save_or_show(fig, output_path / "speed_over_time.png")

    fig, ax = plt.subplots()
    ax.plot(times, power_values + [power_values[-1]] if power_values else [0.0], label="power")
    ax.set_xlabel("Time / s")
    ax.set_ylabel("Power / W")
    ax.grid(True)
    fig.tight_layout()
    _save_or_show(fig, output_path / "power_over_time.png")

    fig, ax = plt.subplots()
    ax.plot(simulator.time_profile, simulator.soc_profile)
    ax.set_xlabel("Time / s")
    ax.set_ylabel("SoC")
    ax.grid(True)
    fig.tight_layout()
    _save_or_show(fig, output_path / "soc_over_time.png")

    fig, ax = plt.subplots()
    elevations = [point.elevation_m for point in route_data.points]
    ax.plot(range(len(elevations)), elevations)
    ax.set_xlabel("Point index")
    ax.set_ylabel("Elevation / m")
    ax.grid(True)
    fig.tight_layout()
    _save_or_show(fig, output_path / "elevation_profile.png")
