from example_utils import clamp, is_equal_in_tolerance, is_less_equal_in_tol, is_greater_equal_in_tol


def test_clamp_below_limit():
    assert clamp(1.0, 0.0, 2.0) == 1.0


def test_clamp_within_range():
    assert clamp(1.5, 0.0, 2.0) == 1.5


def test_clamp_above_limit():
    assert clamp(3.0, 0.0, 2.0) == 2.0


def test_tolerance_helpers():
    assert is_equal_in_tolerance(1.0, 1.0 + 1e-10)
    assert is_less_equal_in_tol(1.0, 1.0 + 1e-10)
    assert is_greater_equal_in_tol(1.0 + 1e-10, 1.0)
