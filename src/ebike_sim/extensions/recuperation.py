"""Extension module for recuperation modeling.

Converts available braking power into a charging current for the battery,
accounting for conversion losses (efficiency) and a maximum charge current
limit imposed by the battery/charge controller.
"""

from __future__ import annotations

import math

def calculate_recuperation_current(
    mechanical_power_w: float,
    terminal_voltage_v: float,
    efficiency: float,
    maximum_charge_current_a: float,
) -> float:
    """Calculate the charging current from available braking power."""
    values = (mechanical_power_w, terminal_voltage_v, efficiency, maximum_charge_current_a)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("All input values must be finite numbers.")
    if mechanical_power_w < 0.0:
        raise ValueError("Mechanical power must not be negative.")
    if terminal_voltage_v <= 0.0:
        raise ValueError("Terminal voltage must be greater than zero.")
    if not 0.0 <= efficiency <= 1.0:
        raise ValueError("Efficiency must be between 0 and 1.")
    if maximum_charge_current_a <= 0.0:
        raise ValueError("Maximum charge current must not be negative.")
    
    electrical_power_w = mechanical_power_w * efficiency
    current_a = electrical_power_w / terminal_voltage_v
    return min(current_a, maximum_charge_current_a)
