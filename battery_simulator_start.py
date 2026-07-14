from battery_pack_start import BatteryPack

from plotting_utils import (
    plot_current_profile,
    plot_voltage_profile,
    plot_voltage_and_current_profile,
)


class BatterySimulator:
    """Simple simulator for a battery pack. The simulator applies a current profile to the battery pack and records the voltage profile."""

    def __init__(self, battery_pack: BatteryPack) -> None:
        self.battery_pack = battery_pack
        self.current_profile: list[float] = []
        self.duration_profile: list[float] = []
        self.time_profile: list[float] = []
        self.voltage_profile: list[float] = []
        self.soc_profile: list[float] = []

    def simulate(self, current_profile: list[float], duration_profile: list[float]) -> None:
        if len(current_profile) != len(duration_profile):
            raise ValueError("Current and duration profiles must have the same length.")
        if any(duration < 0.0 for duration in duration_profile):
            raise ValueError("Duration values must not be negative.")

        self.current_profile = list(current_profile)
        self.duration_profile = list(duration_profile)
        self.time_profile = []
        self.voltage_profile = []
        self.soc_profile = []

        self.voltage_profile.append(self.battery_pack.voltage(0.0))
        self.soc_profile.append(self.battery_pack.soc)
        self.time_profile.append(0.0)

        elapsed_time = 0.0
        for current, duration in zip(current_profile, duration_profile):
            self.battery_pack.apply_current(current=current, duration=duration)
            elapsed_time += duration
            self.time_profile.append(elapsed_time)
            self.voltage_profile.append(self.battery_pack.voltage(current))
            self.soc_profile.append(self.battery_pack.soc)

        if self.battery_pack.is_empty():
            print("Warning: Battery is empty after simulation.")
        if self.battery_pack.is_full():
            print("Warning: Battery is full after simulation.")


if __name__ == "__main__":
    load_current = [3.0, 11.0, 4.0, -1.5, 1.0]
    load_durations = [300.0, 240.0, 90.0, 150.0, 120.0]

    plot_current_profile(current_profile=load_current, duration_profile=load_durations)

    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7, Vmin=32.0, Vmax=42.0)
    bat_sim = BatterySimulator(battery)
    bat_sim.simulate(load_current, load_durations)
    print(battery)

    plot_voltage_profile(voltage_profile=bat_sim.voltage_profile, duration_profile=load_durations)
    plot_voltage_and_current_profile(bat_sim.voltage_profile, load_current, load_durations)

    if __import__("sys").stdin.isatty():
        input("Press Enter to continue...")
    else:
        print("Simulation complete.")