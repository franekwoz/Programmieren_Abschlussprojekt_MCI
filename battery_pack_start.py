from math import isfinite

from example_utils import clamp


class BatteryPack:
    """
    Simple model of a battery pack as a single cell.
    The battery is modeled as an ideal voltage source (open circuit voltage) in series with an internal resistance.
    The open circuit voltage is a linear function of the state of charge (SoC).
    The SoC is updated based on the applied current and duration.
    """

    def __init__(
        self,
        capacity_nom_Ah: float = 10.0,
        internal_resistance_mOhm: float = 80.0,
        initial_soc: float = 1.0,
        Vmin: float = 3.0,
        Vmax: float = 4.2,
    ):
        self._validate_inputs(capacity_nom_Ah, internal_resistance_mOhm, initial_soc, Vmin, Vmax)
        self.capacity_nom_Ah = float(capacity_nom_Ah)
        self.internal_resistance_mOhm = float(internal_resistance_mOhm)
        self.initial_soc = float(initial_soc)
        self.Vmin = float(Vmin)
        self.Vmax = float(Vmax)
        self.soc = self.initial_soc

    @staticmethod
    def _validate_inputs(capacity_nom_Ah: float, internal_resistance_mOhm: float, initial_soc: float, Vmin: float, Vmax: float) -> None:
        values = [capacity_nom_Ah, internal_resistance_mOhm, initial_soc, Vmin, Vmax]
        if any(not isfinite(value) for value in values):
            raise ValueError("All battery parameters must be finite values.")
        if capacity_nom_Ah <= 0.0:
            raise ValueError("capacity_nom_Ah must be greater than zero.")
        if internal_resistance_mOhm < 0.0:
            raise ValueError("internal_resistance_mOhm must not be negative.")
        if not 0.0 <= initial_soc <= 1.0:
            raise ValueError("initial_soc must be between 0 and 1.")
        if Vmax <= Vmin:
            raise ValueError("Vmax must be greater than Vmin.")

    def apply_current(self, current: float, duration: float) -> None:
        """Modify the SoC based on the applied current & duration."""
        if not isfinite(current):
            raise ValueError("current must be finite.")
        if not isfinite(duration):
            raise ValueError("duration must be finite.")
        if duration < 0.0:
            raise ValueError("duration must not be negative.")

        delta_soc = current * duration / (self.capacity_nom_Ah * 3600.0)
        self.soc = clamp(self.soc - delta_soc, 0.0, 1.0)

    def is_empty(self) -> bool:
        return self.soc <= 0.0

    def is_full(self) -> bool:
        return self.soc >= 1.0

    def voltage(self, current: float = 0.0) -> float:
        """Return the current voltage of the battery at the SoC and the given current flow."""
        if not isfinite(current):
            raise ValueError("current must be finite.")
        internal_resistance_ohm = self.internal_resistance_mOhm / 1000.0
        open_circuit_voltage = self.Vmin + self.soc * (self.Vmax - self.Vmin)
        return open_circuit_voltage - current * internal_resistance_ohm

    def __str__(self):
        return f"BatteryPack(SoC={self.soc * 100:.1f}%, V={self.voltage():.2f} V)"


if __name__ == "__main__":

    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7, Vmin=32.0, Vmax=42.0)
    print(battery)

    battery.apply_current(current=5.0, duration=300.0)
    print(battery)
    battery.apply_current(current=10.0, duration=240.0)
    print(battery)
    battery.apply_current(current=-5.0, duration=150.0)

    print(battery)
