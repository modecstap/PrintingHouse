"""Builds impositions from client fields or printer catalog spacing."""

from backend.new_core.equipment.printer import PrinterID
from backend.new_core.equipment.printer_repository import PrinterRepository
from backend.new_core.format import Format
from backend.new_core.materials.sheet import Sheet, SheetID
from backend.new_core.materials.sheet_repository import SheetRepository
from backend.new_core.print_run.imposition import Imposition


class ImpositionFactory:
    """Assembles :class:`Imposition` value objects."""

    def __init__(
        self,
        sheets: SheetRepository,
        printers: PrinterRepository,
    ) -> None:
        self._sheets = sheets
        self._printers = printers

    def create(
        self,
        *,
        target: Format,
        press_sheet: Sheet,
        bleeds: int,
        spacing: int,
    ) -> Imposition:
        """Builds an imposition from the passed fields.

        :param target:
        :param press_sheet:
        :param bleeds:
        :param spacing:

        :raises InvalidInput: if the field combination is not allowed.

        :return: the imposition with the given ``spacing`` and ``press_sheet``.
        """
        return Imposition(
            target=target,
            press_sheet=press_sheet,
            bleeds=bleeds,
            spacing=spacing,
        )

    def create_for_printer(
        self,
        *,
        target: Format,
        sheet_id: SheetID,
        bleeds: int,
        printer_id: PrinterID,
    ) -> Imposition:
        """Builds a hydrated imposition with spacing from the printer catalog.

        :param target:
        :param sheet_id:
        :param bleeds:
        :param printer_id:

        :raises KeyError: if the sheet or printer id is missing.
        :raises InvalidInput: if the assembled layout is not allowed.

        :return: the imposition with catalog ``press_sheet`` and printer
        ``spacing``.
        """
        sheet = self._sheets.take(sheet_id)
        spacing = self._printers.take(printer_id).spacing
        return Imposition(
            target=target,
            press_sheet=sheet,
            bleeds=bleeds,
            spacing=spacing,
        )
