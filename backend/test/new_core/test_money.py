"""Money validation and arithmetic edge cases."""

from decimal import Decimal

import pytest

from backend.new_core.errors import InvalidPriceException
from backend.new_core.values.money import Money


__all__ = [
    "test_rejects_non_decimal_amount",
    "test_rejects_negative_decimal",
    "test_eq_and_add_return_not_implemented_for_other_types",
    "test_mul_and_div_accept_int_and_decimal",
    "test_mul_and_div_return_not_implemented_for_bad_factor",
    "test_mul_accepts_float_factor",
    "test_quantize_rounds_half_up_to_cents",
]

def test_rejects_non_decimal_amount():
    """Handles test rejects non decimal amount.
    """
    with pytest.raises(InvalidPriceException, match="неотрицательным Decimal"):
        Money(1)  # type: ignore[arg-type]


def test_rejects_negative_decimal():
    """Handles test rejects negative decimal.
    """
    with pytest.raises(InvalidPriceException):
        Money(Decimal("-0.01"))


def test_eq_and_add_return_not_implemented_for_other_types():
    """Handles test eq and add return not implemented for other types.
    """
    money = Money(Decimal(1))

    assert money.__eq__(
        42) is NotImplemented  # pylint: disable=unnecessary-dunder-call
    assert money.__add__(
        42) is NotImplemented  # pylint: disable=unnecessary-dunder-call


def test_mul_and_div_accept_int_and_decimal():
    """Handles test mul and div accept int and decimal.
    """
    money = Money(Decimal(10))

    assert (money * 2).amount == Decimal(20)
    assert (money * Decimal("0.5")).amount == Decimal(5)
    assert (money / 4).amount == Decimal("2.5")


def test_mul_and_div_return_not_implemented_for_bad_factor():
    """Handles test mul and div return not implemented for bad factor.
    """
    money = Money(Decimal(1))

    # operator would raise TypeError and hide NotImplemented
    assert money.__mul__(
        object()) is NotImplemented  # pylint: disable=unnecessary-dunder-call
    assert money.__truediv__(
        object()) is NotImplemented  # pylint: disable=unnecessary-dunder-call


def test_mul_accepts_float_factor():
    """Handles test mul accepts float factor.
    """
    assert (Money(Decimal(2)) * 1.5).amount == Decimal(3)


def test_quantize_rounds_half_up_to_cents():
    """Handles test quantize rounds half up to cents.
    """
    assert Money(Decimal("1.005")).amount == Decimal("1.01")
