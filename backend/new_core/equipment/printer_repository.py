"""Printer catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.equipment.printer import Printer, PrinterID


class PrinterRepository(Protocol):
    """Loads printers by id."""

    def take(self, printer_id: PrinterID) -> Printer:
        """Returns the printer with this id.

        :param printer_id:

        :return: the printer row.
        """
        ...
