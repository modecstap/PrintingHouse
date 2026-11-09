"""SQL implementation of ``PrinterRepository``."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.new_core.equipment.printer import Printer, PrinterID
from backend.new_core.equipment.printer_repository import PrinterIdOccupied
from backend.new_core.values.money import Money
from backend.storage.equipment.tables import PrinterRow


class SqlPrinterRepository:
    """Loads and stores printers in PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def take(self, printer_id: PrinterID) -> Printer:
        """Returns the printer with this id.

        :param printer_id:

        :raises KeyError: if there is no printer.

        :return: the printer row.
        """
        row = self._session.get(PrinterRow, printer_id.value)
        if row is None:
            raise KeyError(printer_id)
        return self._printer_from_row(printer_id, row)

    def take_all(self) -> tuple[Printer, ...]:
        """Returns every stored printer.

        :return: printers in ascending id order.
        """
        stmt = select(PrinterRow).order_by(PrinterRow.id)
        rows = self._session.execute(stmt).scalars().all()
        return tuple(
            self._printer_from_row(PrinterID(row.id), row) for row in rows
        )

    def save(self, printer: Printer) -> None:
        """Stores the printer under its id.

        :param printer:

        :raises PrinterIdOccupied: if that id is already stored.

        :return: nothing. Existing rows are not overwritten.
        """
        try:
            self._session.add(
                PrinterRow(
                    id=printer.id.value,
                    startup=printer.startup.amount,
                    cyan=printer.cyan.amount,
                    magenta=printer.magenta.amount,
                    yellow=printer.yellow.amount,
                    black=printer.black.amount,
                ),
            )
            self._session.flush()
        except IntegrityError as exc:
            raise PrinterIdOccupied("save", printer.id) from exc

    def delete(self, printer_id: PrinterID) -> None:
        """Removes the printer with this id.

        :param printer_id:

        :raises KeyError: if there is no printer.

        :return: nothing.
        """
        row = self._session.get(PrinterRow, printer_id.value)
        if row is None:
            raise KeyError(printer_id)
        self._session.delete(row)

    @staticmethod
    def _printer_from_row(printer_id: PrinterID, row: PrinterRow) -> Printer:
        return Printer(
            id=printer_id,
            startup=Money(row.startup),
            cyan=Money(row.cyan),
            magenta=Money(row.magenta),
            yellow=Money(row.yellow),
            black=Money(row.black),
        )
