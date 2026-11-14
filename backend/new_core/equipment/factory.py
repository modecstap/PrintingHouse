"""Builds equipment catalog rows with ids from the store."""

from __future__ import annotations

from backend.new_core.equipment.cutter import Cutter
from backend.new_core.equipment.cutter_repository import CutterRepository
from backend.new_core.equipment.laminator import Laminator
from backend.new_core.equipment.laminator_repository import LaminatorRepository
from backend.new_core.equipment.printer import Printer
from backend.new_core.equipment.printer_repository import PrinterRepository
from backend.new_core.values.money import Money


class PrinterFactory:
    """Allocates printer ids and builds printers."""

    def __init__(self, printers: PrinterRepository) -> None:
        self._printers = printers

    def create(
        self,
        name: str,
        spacing: int,
        startup: Money,
        cyan: Money,
        magenta: Money,
        yellow: Money,
        black: Money,
    ) -> Printer:
        """Builds a printer with a generated id.

        :param name:
        :param spacing:
        :param startup:
        :param cyan:
        :param magenta:
        :param yellow:
        :param black:

        :return: the new printer.
        """
        return Printer(
            id=self._printers.generate_id(),
            name=name,
            spacing=spacing,
            startup=startup,
            cyan=cyan,
            magenta=magenta,
            yellow=yellow,
            black=black,
        )


class LaminatorFactory:
    """Allocates laminator ids and builds laminators."""

    def __init__(self, laminators: LaminatorRepository) -> None:
        self._laminators = laminators

    def create(self, name: str, startup: Money) -> Laminator:
        """Builds a laminator with a generated id.

        :param name:
        :param startup:

        :return: the new laminator.
        """
        return Laminator(
            id=self._laminators.generate_id(),
            name=name,
            startup=startup,
        )


class CutterFactory:
    """Allocates cutter ids and builds cutters."""

    def __init__(self, cutters: CutterRepository) -> None:
        self._cutters = cutters

    def create(self, name: str, max_stack: int) -> Cutter:
        """Builds a cutter with a generated id.

        :param name:
        :param max_stack:

        :return: the new cutter.
        """
        return Cutter(
            id=self._cutters.generate_id(),
            name=name,
            max_stack=max_stack,
        )