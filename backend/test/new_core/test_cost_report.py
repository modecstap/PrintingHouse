"""CostReport operator fallbacks."""

from backend.new_core.accountant.cost_report import CostReport


def test_arithmetic_returns_not_implemented_for_wrong_types():
    report = CostReport.zero()

    assert report.__mul__("bad") is NotImplemented
    assert report.__add__("bad") is NotImplemented
    assert report.__truediv__("bad") is NotImplemented
