from dataclasses import dataclass


@dataclass
class BikeParameters:
    rider_mass_kg: float = 70.0
    bike_mass_kg: float = 10.0
    cw_a_m2: float = 0.5625
    wheel_diameter_inch: float = 27.0
    motor_constant_nm_per_a: float = 1.5
    air_density_kg_m3: float = 1.225
    gravity_m_s2: float = 9.81
    gear_ratio: float = 1.0
    motor_efficiency: float = 1.0

    @property
    def total_mass_kg(self) -> float:
        return self.rider_mass_kg + self.bike_mass_kg

    @property
    def wheel_radius_m(self) -> float:
        return self.wheel_diameter_inch * 0.0254 / 2.0
