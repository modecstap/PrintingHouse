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
            startup=Money(Decimal(0)),
            cyan=Money(Decimal(0)),
            magenta=Money(Decimal(0)),
            yellow=Money(Decimal(0)),
            black=Money(Decimal(0)),
        )
