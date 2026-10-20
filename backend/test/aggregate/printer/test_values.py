from decimal import Decimal

import pytest

from backend.aggregate.printer.errors import (
    InvalidIdException,
    InvalidPriceException,
    InvalidSheetCountException,
)
from backend.aggregate.printer.money import Money
from backend.aggregate.printer.values.ink import Ink
from backend.aggregate.printer.values.printer_id import PrinterID
from backend.aggregate.printer.values.printing_id import PrintingID


def test_money_stores_the_given_decimal():
    assert Money(Decimal("1.23456")).amount == Decimal("1.23456")


def test_money_equality_is_by_amount():
    assert Money(Decimal("20.00")) == Money(Decimal("20"))
    assert Money(Decimal("20")) != Money(Decimal("21"))


def test_money_rejects_negative_amount():
    with pytest.raises(InvalidPriceException):
        Money(Decimal("-0.01"))

    assert Money(Decimal("0")).amount == Decimal("0")


@pytest.mark.parametrize("amount", [1.5, 20, "20", True])
def test_money_rejects_non_decimal(amount):
    with pytest.raises(InvalidPriceException):
        Money(amount)


def test_printer_id_stores_positive_int():
    assert PrinterID(1).value == 1
    assert PrinterID(1) == PrinterID(1)
    assert PrinterID(1) != 1


@pytest.mark.parametrize("value", [0, -1, True, 1.0])
def test_printer_id_rejects_invalid(value):
    with pytest.raises(InvalidIdException):
        PrinterID(value)


def test_printing_id_rejects_zero():
    with pytest.raises(InvalidIdException):
        PrintingID(0)


def test_empty_ink_has_zero_sheets_and_zero_price():
    ink = Ink()

    assert ink.sheet_remains == 0
    assert ink.price == Money(Decimal("0"))


def test_ink_rejects_negative_sheet_remains():
    with pytest.raises(InvalidSheetCountException):
        Ink(-1)
