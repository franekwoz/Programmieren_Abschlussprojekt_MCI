import pytest

from battery_pack_start import BatteryPack


def test_battery_pack_initialization():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7, Vmin=32.0, Vmax=42.0)
    assert battery.capacity_nom_Ah == 10
    assert battery.initial_soc == pytest.approx(0.7)
    assert battery.soc == pytest.approx(0.7)


def test_invalid_capacity():
    with pytest.raises(ValueError):
        BatteryPack(capacity_nom_Ah=0)


def test_invalid_initial_soc():
    with pytest.raises(ValueError):
        BatteryPack(initial_soc=1.2)


def test_soc_decreases_with_positive_current():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7)
    battery.apply_current(5.0, 3600.0)
    assert battery.soc < 0.7


def test_soc_increases_with_negative_current():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.2)
    battery.apply_current(-5.0, 3600.0)
    assert battery.soc > 0.2


def test_soc_is_clamped():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.05)
    battery.apply_current(100.0, 3600.0)
    assert battery.soc == 0.0


def test_voltage_without_load():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7, Vmin=32.0, Vmax=42.0)
    assert battery.voltage(0.0) == pytest.approx(32.0 + 0.7 * (42.0 - 32.0))


def test_voltage_under_load():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7, Vmin=32.0, Vmax=42.0)
    assert battery.voltage(10.0) < battery.voltage(0.0)


def test_is_empty_and_full():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.0)
    assert battery.is_empty()
    assert not battery.is_full()

    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=1.0)
    assert battery.is_full()
    assert not battery.is_empty()


def test_string_representation():
    battery = BatteryPack(capacity_nom_Ah=10, initial_soc=0.7, Vmin=32.0, Vmax=42.0)
    assert "BatteryPack" in str(battery)
