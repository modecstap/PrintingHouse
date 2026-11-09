"""Use cases that list, load, store, and remove equipment catalog rows."""

from __future__ import annotations

from backend.new_core.equipment.cutter import Cutter, CutterID
from backend.new_core.equipment.cutter_repository import CutterRepository
from backend.new_core.equipment.laminator import Laminator, LaminatorID
from backend.new_core.equipment.laminator_repository import LaminatorRepository
from backend.new_core.equipment.printer import Printer, PrinterID
from backend.new_core.equipment.printer_repository import PrinterRepository


class EquipmentCatalogService:
    """Loads and edits printers, laminators, and cutters."""

    def __init__(
        self,
        printers: PrinterRepository,
        laminators: LaminatorRepository,
        cutters: CutterRepository,
    ) -> None:
        """Remembers the equipment stores.

        :param printers:
        :param laminators:
        :param cutters:
        """
        self._printers = printers
        self._laminators = laminators
        self._cutters = cutters

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

    def delete_printer(self, printer_id: PrinterID) -> None:
        """Removes a printer.

        :param printer_id:

        :raises KeyError: if there is no printer.

        :return: nothing.
        """
        self._printers.delete(printer_id)

    def laminators(self) -> tuple[Laminator, ...]:
        """Returns every stored laminator.

        :return: laminators in ascending id order.
        """
        return self._laminators.take_all()

    def laminator(self, laminator_id: LaminatorID) -> Laminator:
        """Returns one laminator.

        :param laminator_id:

        :raises KeyError: if there is no laminator.

        :return: the laminator row.
        """
        return self._laminators.take(laminator_id)

    def save_laminator(self, laminator: Laminator) -> None:
        """Stores a new laminator under its id.

        :param laminator:

        :return: nothing. Existing rows are not overwritten.
        """
        self._laminators.save(laminator)

    def delete_laminator(self, laminator_id: LaminatorID) -> None:
        """Removes a laminator.

        :param laminator_id:

        :raises KeyError: if there is no laminator.

        :return: nothing.
        """
        self._laminators.delete(laminator_id)

    def cutters(self) -> tuple[Cutter, ...]:
        """Returns every stored cutter.

        :return: cutters in ascending id order.
        """
        return self._cutters.take_all()

    def cutter(self, cutter_id: CutterID) -> Cutter:
        """Returns one cutter.

        :param cutter_id:

        :raises KeyError: if there is no cutter.

        :return: the cutter row.
        """
        return self._cutters.take(cutter_id)

    def save_cutter(self, cutter: Cutter) -> None:
        """Stores a new cutter under its id.

        :param cutter:

        :return: nothing. Existing rows are not overwritten.
        """
        self._cutters.save(cutter)

    def delete_cutter(self, cutter_id: CutterID) -> None:
        """Removes a cutter.

        :param cutter_id:

        :raises KeyError: if there is no cutter.

        :return: nothing.
        """
        self._cutters.delete(cutter_id)
