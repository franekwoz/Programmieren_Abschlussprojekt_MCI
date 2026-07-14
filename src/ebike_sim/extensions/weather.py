"""Extension module for optional weather-aware simulations.

TODO(extension): add wind speed, wind direction, headwind/tailwind handling, and optional weather data files without network access.
"""

from __future__ import annotations


def __getattr__(name: str):
    raise NotImplementedError("Weather support is not implemented yet")
