"""Catalog entities reject a blank name."""

import pytest

from backend.new_core.equipment.printer import Printer, PrinterID
from backend.new_core.errors import InvalidInput
from backend.test.storage.helpers import zero_printer_prices


def test_printer_rejects_blank_name():
    """Whitespace-only name raises InvalidInput."""
    with pytest.raises(InvalidInput, match="printer: название не задано"):
        Printer(
            id=PrinterID(1),
            name="   ",
            spacing=0,
            prices=zero_printer_prices(),
        )


def test_printer_rejects_negative_spacing():
    """Negative spacing raises InvalidInput with field message."""
    with pytest.raises(InvalidInput, match="поля меньше 0"):
        Printer(
            id=PrinterID(1),
            name="printer",
            spacing=-1,
            prices=zero_printer_prices(),
        )
