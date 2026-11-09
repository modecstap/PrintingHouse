"""Money validation and arithmetic edge cases."""

from decimal import Decimal

import pytest

from backend.new_core.errors import InvalidPriceException
from backend.new_core.values.money import Money


def test_rejects_non_decimal_amount():
    with pytest.raises(InvalidPriceException, match="неотрицательным Decimal"):
        Money(1)  # type: ignore[arg-type]


def test_rejects_negative_decimal():
    with pytest.raises(InvalidPriceException):
        Money(Decimal("-0.01"))


def test_eq_and_add_return_not_implemented_for_other_types():
    money = Money(Decimal(1))

    assert money.__eq__(42) is NotImplemented
    assert money.__add__(42) is NotImplemented


def test_mul_and_div_accept_int_and_decimal():
    money = Money(Decimal(10))

    assert (money * 2).amount == Decimal(20)
    assert (money * Decimal("0.5")).amount == Decimal(5)
    assert (money / 4).amount == Decimal("2.5")


def test_mul_and_div_return_not_implemented_for_bad_factor():
    money = Money(Decimal(1))

    assert money.__mul__(object()) is NotImplemented
    assert money.__truediv__(object()) is NotImplemented


def test_mul_accepts_float_factor():
    assert (Money(Decimal(2)) * 1.5).amount == Decimal(3)


def test_quantize_rounds_half_up_to_cents():
    assert Money(Decimal("1.005")).quantize().amount == Decimal("1.01")
