"""Extension module for temperature-dependent battery behavior.

TODO(extension): model temperature-dependent resistance and capacity, define temperature limits, and use GPS temperature values per segment.
"""

from __future__ import annotations


def calculate_temperature_adjusted_resistance(reference_resistance_ohm: float, temperature_c: float) -> float:
    raise NotImplementedError("Temperature-adjusted resistance is not implemented yet")


def calculate_temperature_adjusted_capacity(reference_capacity_ah: float, temperature_c: float) -> float:
    raise NotImplementedError("Temperature-adjusted capacity is not implemented yet")
