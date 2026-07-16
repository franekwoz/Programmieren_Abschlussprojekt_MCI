from __future__ import annotations
import math

SEA_LEVEL_PRESSURE_PA = 101_325.0       #Luftdruck auf Meereshöhe in Pascal
SPECIFIC_GAS_CONSTANT_DRY_AIR = 287.05  # J / (kg*K) spezifische Gaskonstante für trockene Luft
GRAVITY_M_S2 = 9.81                     #Erdbeschleunigung in m/s²
CELSIUS_TO_KELVIN_OFFSET = 273.15       # Umrechnungsfaktor von Celsius zu Kelvin


def calculate_air_density(elevation_m: float, temperature_c: float) -> float:
    """Calculate air density based on elevation and temperature.

    Args:
        elevation_m (float): Elevation in meters.
        temperature_c (float): Temperature in degrees Celsius.

    Returns:
        float: Air density in kg/m³.
    """
    if not math.isfinite(elevation_m) or not math.isfinite(temperature_c):      #Scheckung auf endliche Werte -> mathematische Fehler vermeiden
        raise ValueError("elevation_m and temperature_c must be finite values.")

    temperature_k = temperature_c + CELSIUS_TO_KELVIN_OFFSET
    if temperature_k <= 0.0:
        raise ValueError("temperature_c must be above absolute zero.")

    pressure_pa = SEA_LEVEL_PRESSURE_PA * math.exp(
        -GRAVITY_M_S2 * elevation_m / (SPECIFIC_GAS_CONSTANT_DRY_AIR * temperature_k)  #barometrische Höhenformel: p(h) = p₀ · e^(−g·h / (R·T))
    )

    return pressure_pa / (SPECIFIC_GAS_CONSTANT_DRY_AIR * temperature_k)