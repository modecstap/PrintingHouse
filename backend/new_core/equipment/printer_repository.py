"""Printer catalog contract."""

from __future__ import annotations

from typing import Literal, Protocol

from backend.new_core.catalog.errors import CatalogIdOccupied
from backend.new_core.equipment.printer import Printer, PrinterID

PrinterStoreOperation = Literal["save"]


class PrinterIdOccupied(CatalogIdOccupied):
    """Reports that a printer id is already stored."""

    def __init__(
        self,
        operation: PrinterStoreOperation,
        printer_id: PrinterID,
    ) -> None:
        """Builds the repository error text.

        :param operation:
        :param printer_id:

        :return: sets the message
        ``{operation}: принтер уже есть, id={printer_id.value}``.
        """
        super().__init__(
            f"{operation}: принтер уже есть, id={printer_id.value}",
        )


class PrinterRepository(Protocol):
    """Loads and stores printers by id."""

    def take(self, printer_id: PrinterID) -> Printer:
        """Returns the printer with this id.

        :param printer_id:

        :raises KeyError: if there is no printer.

        :return: the printer row.
        """
        ...

    def take_all(self) -> tuple[Printer, ...]:
        """Returns every stored printer.

        :return: printers in ascending id order.
        """
        ...

    def save(self, printer: Printer) -> None:
        """Stores the printer under its id.

        :param printer:

        :raises PrinterIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        ...

    def delete(self, printer_id: PrinterID) -> None:
        """Removes the printer with this id.

        :param printer_id:

        :raises KeyError: if there is no printer.

        :return: nothing.
        """
        ...
