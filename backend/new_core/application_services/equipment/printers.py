"""Printer catalog use cases."""

from __future__ import annotations

from backend.new_core.equipment.factory import PrinterFactory
from backend.new_core.equipment.printer import Printer, PrinterID, PrinterPrices
from backend.new_core.equipment.printer_repository import PrinterRepository


__all__ = ["PrinterCatalog"]

class PrinterCatalog:
    """Loads and edits printers."""

    def __init__(
        self,
        printers: PrinterRepository,
        printer_factory: PrinterFactory,
    ) -> None:
        """Remembers the printer store.

        :param printers: the printers.
        :param printer_factory: the printer factory.
        """
        self._printers = printers
        self._printer_factory = printer_factory

    def printers(self) -> tuple[Printer, ...]:
        """Returns every stored printer.

        :return: the tuple[Printer, ...] result.
        """
        return self._printers.take_all()

    def printer(self, printer_id: PrinterID) -> Printer:
        """Returns one printer.

        :param printer_id: id of the printer.

        :raises KeyError: if there is no printer.

        :return: the Printer result.
        """
        return self._printers.take(printer_id)

    def save_printer(self, printer: Printer) -> None:
        """Stores a new printer under its id.

        :param printer: the printer.
        """
        self._printers.save(printer)

    def create_printer(
        self,
        name: str,
        prices: PrinterPrices,
    ) -> PrinterID:
        """Inserts a new printer; the store assigns the id.

        :param name: the name.
        :param prices: the prices.

        :return: the PrinterID result.
        """
        printer = self._printer_factory.create(
            name,
            prices,
        )
        self._printers.save(printer)
        return printer.id

    def replace_printer(self, printer: Printer) -> None:
        """Overwrites non-id fields of an existing printer.

        :param printer:

        :raises KeyError: if there is no printer with this id.
        """
        self._printers.replace(printer)

    def delete_printer(self, printer_id: PrinterID) -> None:
        """Removes a printer.

        :param printer_id:

        :raises KeyError: if there is no printer.
        """
        self._printers.delete(printer_id)
