"""Catalog entities reject a blank name."""

import pytest

from backend.new_core.equipment.printer import Printer, PrinterID
from backend.new_core.errors import InvalidInput
from backend.test.storage.helpers import zero_printer_prices


__all__ = [
    "test_printer_rejects_blank_name",
]


def test_printer_rejects_blank_name():
    """Whitespace-only name raises InvalidInput."""
    with pytest.raises(InvalidInput, match="printer: название не задано"):
        Printer(
            id=PrinterID(1),
            name="   ",
            prices=zero_printer_prices(),
        )