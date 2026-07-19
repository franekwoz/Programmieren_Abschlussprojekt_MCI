"""Extension module for a dissipative braking resistor."""

from __future__ import annotations

import math

def calculate_braking_resistor_power(braking_power_w: float, rechargeable_power_w: float = 0.0) -> float:
    if not math.isfinite(braking_power_w) or not math.isfinite(rechargeable_power_w):
        raise ValueError("breaking_power_w and rechargeable_power_w must be finite numbers.")
    if braking_power_w < 0.0:
        raise ValueError("breaking_power_w must not be negative.")
    if rechargeable_power_w < 0.0:
        raise ValueError("rechargeable_power_w must not be negative.")
    
    return max(braking_power_w - rechargeable_power_w, 0.0)
