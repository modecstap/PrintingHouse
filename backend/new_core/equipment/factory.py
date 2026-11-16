"""Builds equipment catalog rows with ids from the store."""

from __future__ import annotations

from backend.new_core.equipment.cutter import Cutter
from backend.new_core.equipment.cutter_repository import CutterRepository
from backend.new_core.equipment.laminator import Laminator
from backend.new_core.equipment.laminator_repository import LaminatorRepository
from backend.new_core.equipment.printer import Printer, PrinterPrices
from backend.new_core.equipment.printer_repository import PrinterRepository
from backend.new_core.values.money import Money


__all__ = [
    "PrinterFactory",
    "LaminatorFactory",
    "CutterFactory",
]

class PrinterFactory:
    """Allocates printer ids and builds printers."""

    def __init__(self, printers: PrinterRepository) -> None:
        """Initializes this instance.

        :param printers: the printers.
        """
        self._printers = printers

    def create(
        self,
        name: str,
        spacing: int,
        prices: PrinterPrices,
    ) -> Printer:
        """Builds a printer with a generated id.

        :param name: the name.
        :param spacing: the spacing.
        :param prices: the prices.

        :return: the Printer result.
        """
        return Printer(
            id=self._printers.generate_id(),
            name=name,
            spacing=spacing,
            prices=prices,
        )


class LaminatorFactory:
    """Allocates laminator ids and builds laminators."""

    def __init__(self, laminators: LaminatorRepository) -> None:
        """Initializes this instance.

        :param laminators: the laminators.
        """
        self._laminators = laminators

    def create(self, name: str, startup: Money) -> Laminator:
        """Builds a laminator with a generated id.

        :param name: the name.
        :param startup: the startup.

        :return: the Laminator result.
        """
        return Laminator(
            id=self._laminators.generate_id(),
            name=name,
            startup=startup,
        )


class CutterFactory:
    """Allocates cutter ids and builds cutters."""

    def __init__(self, cutters: CutterRepository) -> None:
        """Initializes this instance.

        :param cutters: the cutters.
        """
        self._cutters = cutters

    def create(self, name: str, max_stack: int) -> Cutter:
        """Builds a cutter with a generated id.

        :param name: the name.
        :param max_stack: the max stack.

        :return: the Cutter result.
        """
        return Cutter(
            id=self._cutters.generate_id(),
            name=name,
            max_stack=max_stack,
        )
