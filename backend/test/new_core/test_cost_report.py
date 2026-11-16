"""CostReport operator fallbacks."""

from backend.new_core.accountant.cost_report import CostReport


__all__ = ["test_arithmetic_returns_not_implemented_for_wrong_types"]

def test_arithmetic_returns_not_implemented_for_wrong_types():
    """Handles test arithmetic returns not implemented for wrong types.
    """
    report = CostReport.zero()

    # operator would raise TypeError and hide NotImplemented
    assert report.__mul__(
        "bad") is NotImplemented  # pylint: disable=unnecessary-dunder-call
    assert report.__add__(
        "bad") is NotImplemented  # pylint: disable=unnecessary-dunder-call
    assert report.__truediv__(
        "bad") is NotImplemented  # pylint: disable=unnecessary-dunder-call
