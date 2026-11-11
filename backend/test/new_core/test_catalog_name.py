"""Catalog entities reject a blank name."""

from decimal import Decimal

import pytest

from backend.new_core.equipment.printer import Printer, PrinterID
from backend.new_core.errors import InvalidInput
from backend.new_core.values.money import Money


def test_printer_rejects_blank_name():
    """Whitespace-only name raises InvalidInput."""
    with pytest.raises(InvalidInput, match="printer: название не задано"):
        Printer(
            id=PrinterID(1),
            name="   ",
            spacing=0,
            startup=Money(Decimal(0)),
            cyan=Money(Decimal(0)),
            magenta=Money(Decimal(0)),
            yellow=Money(Decimal(0)),
            black=Money(Decimal(0)),
        )


def test_printer_rejects_negative_spacing():
    """Negative spacing raises InvalidInput with field message."""
    with pytest.raises(InvalidInput, match="поля меньше 0"):
        Printer(
            id=PrinterID(1),
            name="printer",
            spacing=-1,
            startup=Money(Decimal(0)),
            cyan=Money(Decimal(0)),
            magenta=Money(Decimal(0)),
            yellow=Money(Decimal(0)),
            black=Money(Decimal(0)),
        )
