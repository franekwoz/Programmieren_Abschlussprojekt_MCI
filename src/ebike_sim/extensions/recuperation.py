"""Extension module for recuperation modeling.

TODO(extension): detect negative power, apply recuperation efficiency, limit charging current, and respect SoC/voltage limits.
"""

from __future__ import annotations


def calculate_recuperation_current(
    mechanical_power_w: float,
    terminal_voltage_v: float,
    efficiency: float,
    maximum_charge_current_a: float,
) -> float:
    raise NotImplementedError("Recuperation is not implemented yet")
