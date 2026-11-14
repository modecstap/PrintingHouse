"""Use cases that list, load, store, and remove equipment catalog rows."""

from __future__ import annotations

from backend.new_core.equipment.cutter import Cutter, CutterID
from backend.new_core.equipment.cutter_repository import CutterRepository
from backend.new_core.equipment.factory import (
    CutterFactory,
    LaminatorFactory,
    PrinterFactory,
)
from backend.new_core.equipment.laminator import Laminator, LaminatorID
from backend.new_core.equipment.laminator_repository import LaminatorRepository
from backend.new_core.equipment.printer import Printer, PrinterID
from backend.new_core.equipment.printer_repository import PrinterRepository
from backend.new_core.values.money import Money


class EquipmentCatalogService:
    """Loads and edits printers, laminators, and cutters."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        printers: PrinterRepository,
        laminators: LaminatorRepository,
        cutters: CutterRepository,
        printer_factory: PrinterFactory,
        laminator_factory: LaminatorFactory,
        cutter_factory: CutterFactory,
    ) -> None:
        """Remembers the equipment stores.

        :param printers:
        :param laminators:
        :param cutters:
        :param printer_factory:
        :param laminator_factory:
        :param cutter_factory:
        """
        self._printers = printers
        self._laminators = laminators
        self._cutters = cutters
        self._printer_factory = printer_factory
        self._laminator_factory = laminator_factory
        self._cutter_factory = cutter_factory

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
        startup: Money,
        cyan: Money,
        magenta: Money,
        yellow: Money,
        black: Money,
    ) -> PrinterID:
        """Inserts a new printer; the store assigns the id.

        :param name:
        :param spacing:
        :param startup:
        :param cyan:
        :param magenta:
        :param yellow:
        :param black:

        :return: the assigned printer id.
        """
        printer = self._printer_factory.create(
            name,
            spacing,
            startup,
            cyan,
            magenta,
            yellow,
            black,
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

    def create_laminator(self, name: str, startup: Money) -> LaminatorID:
        """Inserts a new laminator; the store assigns the id.

        :param name:
        :param startup:

        :return: the assigned laminator id.
        """
        laminator = self._laminator_factory.create(name, startup)
        self._laminators.save(laminator)
        return laminator.id

    def replace_laminator(self, laminator: Laminator) -> None:
        """Overwrites non-id fields of an existing laminator.

        :param laminator:

        :raises KeyError: if there is no laminator with this id.

        :return: nothing.
        """
        self._laminators.replace(laminator)

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

    def create_cutter(self, name: str, max_stack: int) -> CutterID:
        """Inserts a new cutter; the store assigns the id.

        :param name:
        :param max_stack:

        :return: the assigned cutter id.
        """
        cutter = self._cutter_factory.create(name, max_stack)
        self._cutters.save(cutter)
        return cutter.id

    def replace_cutter(self, cutter: Cutter) -> None:
        """Overwrites non-id fields of an existing cutter.

        :param cutter:

        :raises KeyError: if there is no cutter with this id.

        :return: nothing.
        """
        self._cutters.replace(cutter)

    def delete_cutter(self, cutter_id: CutterID) -> None:
        """Removes a cutter.

        :param cutter_id:

        :raises KeyError: if there is no cutter.

        :return: nothing.
        """
        self._cutters.delete(cutter_id)
