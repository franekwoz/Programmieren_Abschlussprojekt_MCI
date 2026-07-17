"""Extension module for rolling resistance modeling.

Models rolling resistance as a constant coefficient times the slope-adjusted
normal force, added as an additional resisting force alongside aerodynamic
drag and grade force.
"""

from __future__ import annotations
import math


def calculate_rolling_resistance(
    total_mass_kg: float,
    gravity_m_s2: float,
    rolling_coefficient: float,
    slope_angle_rad: float,
) -> float:
    """Estimate the rolling resistance force (N) opposing forward motion."""
    return rolling_coefficient * total_mass_kg * gravity_m_s2 * math.cos(slope_angle_rad)
