"""Maps printer domain objects to SQLAlchemy rows."""

from backend.new_core.equipment.printer import Printer
from backend.storage.equipment.tables import PrinterRow


__all__ = ["new_printer_row"]

def new_printer_row(printer: Printer) -> PrinterRow:
    """Builds a row for inserting or saving a printer."""
    return PrinterRow(
        id=printer.id.value,
        name=printer.name,
        spacing=printer.spacing,
        startup=printer.prices.startup.amount,
        cyan=printer.prices.cyan.amount,
        magenta=printer.prices.magenta.amount,
        yellow=printer.prices.yellow.amount,
        black=printer.prices.black.amount,
    )
