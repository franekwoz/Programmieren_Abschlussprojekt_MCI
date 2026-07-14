"""Extension module for rolling resistance modeling.

TODO(extension): configure rolling resistance coefficients, integrate the force into the ride physics, and model different surfaces.
"""

from __future__ import annotations


def calculate_rolling_resistance(
    total_mass_kg: float,
    gravity_m_s2: float,
    rolling_coefficient: float,
    slope_angle_rad: float,
) -> float:
    raise NotImplementedError("Rolling resistance is not implemented yet")
