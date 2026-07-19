import argparse
import json
import logging
from pathlib import Path
from typing import Optional

import matplotlib
import yaml
matplotlib.use("Agg")

from .analysis.kinematics import calculate_route_data
from .io.gps_reader import read_gps_csv
from .models.battery import LiPoBattery, MMCBattery
from .models.bike_parameters import BikeParameters
from .reporting.exporters import export_summary
from .simulation.battery_simulator import BatterySimulator
from .visualization.plots import create_all_plots


logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a minimal e-bike simulation")
    parser.add_argument("--input", required=True, help="Path to the GPS CSV file")
    parser.add_argument("--battery", choices=["lipo", "mmc", "both"], default="both")
    parser.add_argument("--output", default="outputs")
    parser.add_argument("--bike-config", default="config/bike.yaml", help="Path to bike configuration YAML")
    parser.add_argument("--initial-soc", type=float, default=0.7)
    parser.add_argument("--log-level", default="INFO")
    return parser


def load_bike_parameters(config_path: Path) -> BikeParameters:
    if not config_path.exists():
        logger.warning("Bike config not found at %s. Using default parameters.", config_path)
        return BikeParameters()

    with config_path.open("r", encoding="utf-8") as config_file:
        raw_config = yaml.safe_load(config_file) or {}

    if not isinstance(raw_config, dict):
        raise ValueError(f"Bike config must be a YAML mapping/object, got {type(raw_config).__name__}")

    valid_fields = set(BikeParameters.__dataclass_fields__.keys())
    filtered_values = {key: value for key, value in raw_config.items() if key in valid_fields}
    ignored_keys = sorted(key for key in raw_config if key not in valid_fields)
    if ignored_keys:
        logger.warning("Ignoring unknown bike config keys: %s", ", ".join(ignored_keys))

    return BikeParameters(**filtered_values)


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format="%(levelname)s:%(name)s:%(message)s")

    input_path = Path(args.input)
    output_dir = Path(args.output)
    figures_dir = output_dir / "figures"
    reports_dir = output_dir / "reports"
    logs_dir = output_dir / "logs"
    figures_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(logs_dir / "simulation.log", mode="w")
    file_handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(file_handler)

    logger.info("Reading GPS data from %s", input_path)
    route_data = read_gps_csv(input_path)
    bike_params = load_bike_parameters(Path(args.bike_config))
    logger.info("Using bike parameters from %s", args.bike_config)
    route_data = calculate_route_data(route_data, params=bike_params)
    logger.info("Calculated %d route segments", len(route_data.segments))

    battery_types = []
    if args.battery in {"lipo", "both"}:
        battery_types.append(LiPoBattery(initial_soc=args.initial_soc))
    if args.battery in {"mmc", "both"}:
        battery_types.append(MMCBattery(initial_soc=args.initial_soc))

    summaries = []
    for battery in battery_types:
        battery_key = battery.battery_type.lower()
        battery_figures_dir = figures_dir / battery_key
        battery_reports_dir = reports_dir / battery_key
        simulator = BatterySimulator(battery)
        current_profile = [segment.motor_current_a for segment in route_data.segments]
        duration_profile = [segment.duration_s for segment in route_data.segments]
        temperature_profile = [segment.average_temperature_c for segment in route_data.segments]
        simulator.simulate(current_profile, duration_profile, temperature_profile)
        create_all_plots(route_data, simulator, output_dir=battery_figures_dir)
        summary = export_summary(route_data, simulator, battery, output_dir=battery_reports_dir)
        summaries.append(summary)
        logger.info("Wrote results for battery type %s to %s / %s", battery.battery_type, battery_figures_dir, battery_reports_dir)
    print(json.dumps(summaries, indent=2))
    return 0

if __name__ == "__main__":
    main()
