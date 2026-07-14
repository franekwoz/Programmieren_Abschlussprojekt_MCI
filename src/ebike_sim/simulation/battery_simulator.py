from __future__ import annotations

import math

from ..models.battery import BatteryPack


class BatterySimulator:
    def __init__(self, battery_pack: BatteryPack) -> None:
        self.battery_pack = battery_pack
        self.current_profile: list[float] = []
        self.duration_profile: list[float] = []
        self.time_profile: list[float] = []
        self.voltage_profile: list[float] = []
        self.soc_profile: list[float] = []
        self.distance_profile: list[float] = []
        self.speed_profile: list[float] = []
        self.power_profile: list[float] = []
        self.elevation_profile: list[float] = []
        self.temperature_profile: list[float | None] = []

    def simulate(self, current_profile: list[float], duration_profile: list[float]) -> None:
        if len(current_profile) != len(duration_profile):
            raise ValueError("Current and duration profiles must have the same length.")
        if any(duration < 0.0 for duration in duration_profile):
            raise ValueError("Duration values must not be negative.")

        self.current_profile = list(current_profile)
        self.duration_profile = list(duration_profile)
        self.time_profile = [0.0]
        self.voltage_profile = [self.battery_pack.voltage(0.0)]
        self.soc_profile = [self.battery_pack.soc]
        self.distance_profile = [0.0]
        self.speed_profile = [0.0]
        self.power_profile = [0.0]
        self.elevation_profile = [0.0]
        self.temperature_profile = [None]

        elapsed_time = 0.0
        for current, duration in zip(current_profile, duration_profile):
            self.battery_pack.apply_current(current=current, duration=duration)
            elapsed_time += duration
            self.time_profile.append(elapsed_time)
            self.voltage_profile.append(self.battery_pack.voltage(current))
            self.soc_profile.append(self.battery_pack.soc)
            self.distance_profile.append(self.distance_profile[-1])
            self.speed_profile.append(self.speed_profile[-1])
            self.power_profile.append(self.power_profile[-1])
            self.elevation_profile.append(self.elevation_profile[-1])
            self.temperature_profile.append(None)

        if self.battery_pack.is_empty():
            print("Warning: Battery is empty after simulation.")
        if self.battery_pack.is_full():
            print("Warning: Battery is full after simulation.")
