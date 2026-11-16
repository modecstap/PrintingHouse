"""Printer catalog use cases."""

from __future__ import annotations

from backend.new_core.equipment.factory import PrinterFactory
from backend.new_core.equipment.printer import Printer, PrinterID, PrinterPrices
from backend.new_core.equipment.printer_repository import PrinterRepository


class PrinterCatalog:
    """Loads and edits printers."""

    def __init__(
        self,
        printers: PrinterRepository,
        printer_factory: PrinterFactory,
    ) -> None:
        """Remembers the printer store.

        :param printers:
        :param printer_factory:
        """
        self._printers = printers
        self._printer_factory = printer_factory

    def printers(self) -> tuple[Printer, ...]:
        """Returns every stored printer.

        :return: printers in ascending id order.
        """
        return self._printers.take_all()

    def printer(self, printer_id: PrinterID) -> Printer:
        """Returns one printer.

        :param printer_id:

        :raises KeyError: if there is no printer.

        :return: the printer row.
        """
        return self._printers.take(printer_id)

    def save_printer(self, printer: Printer) -> None:
        """Stores a new printer under its id.

        :param printer:

        :return: nothing. Existing rows are not overwritten.
        """
        self._printers.save(printer)

    def create_printer(
        self,
        name: str,
        spacing: int,
        prices: PrinterPrices,
    ) -> PrinterID:
        """Inserts a new printer; the store assigns the id.

        :param name:
        :param spacing:
        :param prices:

        :return: the assigned printer id.
        """
        printer = self._printer_factory.create(
            name,
            spacing,
            prices,
        )
        self._printers.save(printer)
        return printer.id

    def replace_printer(self, printer: Printer) -> None:
        """Overwrites non-id fields of an existing printer.

        :param printer:

        :raises KeyError: if there is no printer with this id.

        :return: nothing.
        """
        self._printers.replace(printer)

    def delete_printer(self, printer_id: PrinterID) -> None:
        """Removes a printer.

        :param printer_id:

        :raises KeyError: if there is no printer.

        :return: nothing.
        """
        self._printers.delete(printer_id)
