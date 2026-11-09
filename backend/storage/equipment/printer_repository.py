"""SQL implementation of ``PrinterRepository``."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.new_core.equipment.printer import Printer, PrinterID
from backend.new_core.values.money import Money
from backend.storage.equipment.tables import PrinterRow


class SqlPrinterRepository:
    """Loads printers from PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, printer_id: PrinterID) -> Printer:
        """Returns the printer with this id.

        :param printer_id:

        :return: the printer row.
        """
        row = self._session.get(PrinterRow, printer_id.value)
        if row is None:
            raise KeyError(printer_id)
        return Printer(
            id=printer_id,
            startup=Money(row.startup),
            cyan=Money(row.cyan),
            magenta=Money(row.magenta),
            yellow=Money(row.yellow),
            black=Money(row.black),
        )
