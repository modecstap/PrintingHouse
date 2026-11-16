"""Printer catalog contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.equipment.printer import Printer, PrinterID

__all__ = [
    "PrinterIdOccupied",
    "PrinterRepository",
]

PrinterStoreOperation = Literal["save"]


class PrinterIdOccupied(CatalogIdOccupied):
    """Reports that a printer id is already stored."""

    def __init__(
        self,
        operation: PrinterStoreOperation,
        printer_id: PrinterID,
    ) -> None:
        """Builds the repository error text.

        :param operation: the operation.
        :param printer_id: id of the printer.
        """
        super().__init__(
            f"{operation}: принтер уже есть, id={printer_id.value}",
        )


class PrinterRepository(Protocol):
    """Loads and stores printers by id."""

    def take(self, printer_id: PrinterID) -> Printer:
        """Returns the printer with this id.

        :param printer_id: id of the printer.

        :raises KeyError: if there is no printer.
"""
        ...

    def take_all(self) -> tuple[Printer, ...]:
        """Returns every stored printer.
"""
        ...

    def generate_id(self) -> PrinterID:
        """Returns the next printer id from the store sequence.
"""
        ...

    def save(self, printer: Printer) -> None:
        """Stores the printer under its id.

        :param printer:

        :raises PrinterIdOccupied: if that id is already stored.
        """
        ...

    def replace(self, printer: Printer) -> None:
        """Overwrites non-id fields of an existing printer.

        :param printer:

        :raises KeyError: if there is no printer with this id.
        """
        ...

    def delete(self, printer_id: PrinterID) -> None:
        """Removes the printer with this id.

        :param printer_id:

        :raises KeyError: if there is no printer.
        """
        ...
