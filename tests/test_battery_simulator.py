import pytest

from battery_pack_start import BatteryPack
from battery_simulator_start import BatterySimulator


def test_simulator_profiles_match_lengths():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7)
    simulator = BatterySimulator(battery)
    simulator.simulate([1.0, 2.0], [10.0, 20.0])
    assert len(simulator.current_profile) == 2
    assert len(simulator.voltage_profile) == 3
    assert len(simulator.soc_profile) == 3


def test_simulator_raises_on_different_lengths():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7)
    simulator = BatterySimulator(battery)
    with pytest.raises(ValueError):
        simulator.simulate([1.0], [10.0, 20.0])


def test_simulator_raises_on_negative_durations():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7)
    simulator = BatterySimulator(battery)
    with pytest.raises(ValueError):
        simulator.simulate([1.0], [-1.0])


def test_simulator_reuses_clean_state():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7)
    simulator = BatterySimulator(battery)
    simulator.simulate([1.0], [10.0])
    simulator.simulate([2.0], [5.0])
    assert simulator.current_profile == [2.0]
    assert simulator.duration_profile == [5.0]
    assert simulator.time_profile == [0.0, 5.0]
    assert len(simulator.voltage_profile) == 2


def test_simulator_can_empty_battery():
    battery = BatteryPack(capacity_nom_Ah=1, initial_soc=0.5)
    simulator = BatterySimulator(battery)
    simulator.simulate([10.0], [3600.0])
    assert battery.is_empty()
