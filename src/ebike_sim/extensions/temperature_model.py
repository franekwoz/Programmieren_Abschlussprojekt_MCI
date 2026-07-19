"""Extension module for temperature-dependent battery behavior.

TODO(extension): model temperature-dependent resistance and capacity, define temperature limits, and use GPS temperature values per segment.
"""

from __future__ import annotations
import math

REFERENCE_TEMPERATURE_C = 25.0 #Insustriel standard reference temperature for battery performance
RESISTANCE_TEMPERATURE_COEFFICIENT_PER_C = 0.02
CAPACITY_TEMPERATURE_COEFFICIENT_PER_C = 0.008
MIN_RESISTANCE_RATIO = 0.5
MIN_CAPACITY_RATIO = 0.5

def calculate_temperature_adjusted_resistance(reference_resistance_ohm: float, temperature_c: float) -> float:
    """Calculate the temperature-adjusted resistance of a battery."""
    if not math.isfinite(reference_resistance_ohm) or not math.isfinite(temperature_c):
        raise ValueError("reference_resistance_ohm and temperature_c must be finite numbers.")
    if reference_resistance_ohm < 0:
        raise ValueError("reference_resistance_ohm must not be negative.")

    temperature_delta_c = REFERENCE_TEMPERATURE_C - temperature_c
    resistance_ratio = 1.0 + RESISTANCE_TEMPERATURE_COEFFICIENT_PER_C * temperature_delta_c
    resistance_ratio = max(resistance_ratio, MIN_RESISTANCE_RATIO)
    return reference_resistance_ohm * resistance_ratio


def calculate_temperature_adjusted_capacity(reference_capacity_ah: float, temperature_c: float) -> float:
    """Calculate the temperature-adjusted capacity of a battery."""
    if not math.isfinite(reference_capacity_ah) or not math.isfinite(temperature_c): 
        raise ValueError("reference_capacity_ah and temperature_c must be finite numbers.")
    if reference_capacity_ah <= 0: 
        raise ValueError("reference_capacity_ah must be greater than zero.")
    
    temperature_delta_c = max(REFERENCE_TEMPERATURE_C - temperature_c, 0.0)
    capacity_ratio = 1.0 - CAPACITY_TEMPERATURE_COEFFICIENT_PER_C * temperature_delta_c
    capacity_ratio = max(capacity_ratio, MIN_CAPACITY_RATIO)
    return reference_capacity_ah * capacity_ratio
