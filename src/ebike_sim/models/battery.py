from __future__ import annotations

import math
from dataclasses import dataclass

from example_utils import clamp


class BatteryPack:
    """Base battery pack model used by the minimal simulation."""

    def __init__(self, capacity_nom_Ah: float, initial_soc: float = 1.0, internal_resistance_ohm: float = 0.0):
        self.capacity_nom_Ah = float(capacity_nom_Ah)
        self.initial_soc = float(initial_soc)
        self.soc = float(initial_soc)
        self.internal_resistance_ohm = float(internal_resistance_ohm)
        self.battery_type = "base"

    def reset(self, initial_soc: float | None = None) -> None:
        self.soc = self.initial_soc if initial_soc is None else float(initial_soc)

    def apply_current(self, current: float, duration: float) -> None:
        delta_soc = current * duration / (self.capacity_nom_Ah * 3600.0)
        self.soc = clamp(self.soc - delta_soc, 0.0, 1.0)

    def is_empty(self) -> bool:
        return self.soc <= 0.0

    def is_full(self) -> bool:
        return self.soc >= 1.0

    def open_circuit_voltage(self) -> float:
        return 0.0

    def voltage(self, current: float = 0.0) -> float:
        return self.open_circuit_voltage() - current * self.internal_resistance_ohm

    def pack_internal_resistance_ohm(self) -> float:
        return self.internal_resistance_ohm

    def __str__(self) -> str:
        return f"BatteryPack(type={self.battery_type}, soc={self.soc:.2f})"


@dataclass
class BatteryTypeConfig:
    series_cells: int
    parallel_cells: int
    capacity_nom_Ah: float
    initial_soc: float
    cell_internal_resistance_ohm: float
    soc_support_points: list[float]
    cell_ocv_support_points: list[float]


class LiPoBattery(BatteryPack):
    def __init__(self, initial_soc: float = 0.7):
        super().__init__(capacity_nom_Ah=10.0, initial_soc=initial_soc, internal_resistance_ohm=0.008)
        self.battery_type = "LiPo"
        self.series_cells = 10
        self.parallel_cells = 1
        self.cell_internal_resistance_ohm = 0.008
        self.soc_support_points = [0.0, 0.04, 0.09, 0.13, 0.17, 0.21, 0.26, 0.30, 0.40, 0.52, 0.64, 0.76, 0.88, 1.00]
        self.cell_ocv_support_points = [3.2, 3.587, 3.685, 3.756, 3.787, 3.828, 3.881, 3.905, 3.955, 4.027, 4.070, 4.116, 4.165, 4.200]

    def open_circuit_voltage(self) -> float:
        return self._interpolate_cell_voltage(self.soc) * self.series_cells

    def _interpolate_cell_voltage(self, soc: float) -> float:
        soc = clamp(soc, 0.0, 1.0)
        if soc <= self.soc_support_points[0]:
            return self.cell_ocv_support_points[0]
        if soc >= self.soc_support_points[-1]:
            return self.cell_ocv_support_points[-1]
        for idx in range(len(self.soc_support_points) - 1):
            x0 = self.soc_support_points[idx]
            x1 = self.soc_support_points[idx + 1]
            if x0 <= soc <= x1:
                y0 = self.cell_ocv_support_points[idx]
                y1 = self.cell_ocv_support_points[idx + 1]
                fraction = (soc - x0) / (x1 - x0)
                return y0 + fraction * (y1 - y0)
        return self.cell_ocv_support_points[-1]

    def voltage(self, current: float = 0.0) -> float:
        return self.open_circuit_voltage() - current * self.pack_internal_resistance_ohm()

    def pack_internal_resistance_ohm(self) -> float:
        return self.cell_internal_resistance_ohm * self.series_cells / self.parallel_cells


class MMCBattery(BatteryPack):
    def __init__(self, initial_soc: float = 0.7):
        super().__init__(capacity_nom_Ah=10.0, initial_soc=initial_soc, internal_resistance_ohm=0.007)
        self.battery_type = "MMC"
        self.series_cells = 10
        self.parallel_cells = 1
        self.cell_internal_resistance_ohm = 0.007
        self.soc_support_points = [0.0, 0.04, 0.09, 0.13, 0.17, 0.21, 0.26, 0.30, 0.40, 0.52, 0.64, 0.76, 0.88, 1.00]
        self.cell_ocv_support_points = [3.2, 3.261, 3.317, 3.385, 3.424, 3.466, 3.539, 3.565, 3.665, 3.764, 3.891, 4.014, 4.108, 4.200]

    def open_circuit_voltage(self) -> float:
        return self._interpolate_cell_voltage(self.soc) * self.series_cells

    def _interpolate_cell_voltage(self, soc: float) -> float:
        soc = clamp(soc, 0.0, 1.0)
        if soc <= self.soc_support_points[0]:
            return self.cell_ocv_support_points[0]
        if soc >= self.soc_support_points[-1]:
            return self.cell_ocv_support_points[-1]
        for idx in range(len(self.soc_support_points) - 1):
            x0 = self.soc_support_points[idx]
            x1 = self.soc_support_points[idx + 1]
            if x0 <= soc <= x1:
                y0 = self.cell_ocv_support_points[idx]
                y1 = self.cell_ocv_support_points[idx + 1]
                fraction = (soc - x0) / (x1 - x0)
                return y0 + fraction * (y1 - y0)
        return self.cell_ocv_support_points[-1]

    def voltage(self, current: float = 0.0) -> float:
        return self.open_circuit_voltage() - current * self.pack_internal_resistance_ohm()

    def pack_internal_resistance_ohm(self) -> float:
        return self.cell_internal_resistance_ohm * self.series_cells / self.parallel_cells
