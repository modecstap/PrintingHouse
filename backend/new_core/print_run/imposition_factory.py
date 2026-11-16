"""Builds impositions from client fields or printer catalog spacing."""

from dataclasses import dataclass

from backend.new_core.equipment.printer import PrinterID
from backend.new_core.equipment.printer_repository import PrinterRepository
from backend.new_core.format import Format
from backend.new_core.materials.sheet import SheetID
from backend.new_core.materials.sheet_repository import SheetRepository
from backend.new_core.print_run.imposition import Imposition


@dataclass(frozen=True)
class CatalogImposition:  # pylint: disable=too-few-public-methods
    """Target layout, sheet, bleeds, and printer for catalog spacing."""

    target: Format
    sheet_id: SheetID
    bleeds: int
    printer_id: PrinterID


class ImpositionFactory:
    """Assembles :class:`Imposition` value objects."""

    def __init__(
        self,
        sheets: SheetRepository,
        printers: PrinterRepository,
    ) -> None:
        self._sheets = sheets
        self._printers = printers

    def create_for_printer(
        self,
        request: CatalogImposition,
    ) -> Imposition:
        """Builds a hydrated imposition with spacing from the printer catalog.

        :param request: layout fields and printer id.

        :raises KeyError: if the sheet or printer id is missing.
        :raises InvalidInput: if the assembled layout is not allowed.

        :return: the imposition with catalog ``press_sheet`` and printer
        ``spacing``.
        """
        sheet = self._sheets.take(request.sheet_id)
        spacing = self._printers.take(request.printer_id).spacing
        return Imposition(
            target=request.target,
            press_sheet=sheet,
            bleeds=request.bleeds,
            spacing=spacing,
        )