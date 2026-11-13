"""Builds pricing strategies for run operations from catalog repositories."""

from __future__ import annotations

from backend.new_core.accountant.pricing.cut_pricing import CutPricing
from backend.new_core.accountant.pricing.die_cut_pricing import DieCutPricing
from backend.new_core.accountant.pricing.laminate_pricing import LaminatePricing
from backend.new_core.accountant.pricing.print_pricing import PrintPricing
from backend.new_core.accountant.pricing_strategy import PricingStrategy
from backend.new_core.equipment.cutter_repository import CutterRepository
from backend.new_core.equipment.laminator_repository import LaminatorRepository
from backend.new_core.equipment.printer_repository import PrinterRepository
from backend.new_core.materials.film_repository import FilmRepository
from backend.new_core.operations.cut.cut import Cut
from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.operations.laminate.laminate import Laminate
from backend.new_core.operations.print.print import Print
from backend.new_core.personal.cutter_operator_repository import CutterOperatorRepository
from backend.new_core.personal.die_cutter_operator_repository import (
    DieCutterOperatorRepository,
)
from backend.new_core.personal.laminator_operator_repository import (
    LaminatorOperatorRepository,
)
from backend.new_core.personal.press_operator_repository import PressOperatorRepository
from backend.new_core.print_run.print_run import PrintRun


class PricingStrategyFactory:
    """Resolves catalog rows and builds one pricing strategy per operation."""

    def __init__(
        self,
        printers: PrinterRepository,
        press_operators: PressOperatorRepository,
        laminators: LaminatorRepository,
        laminator_operators: LaminatorOperatorRepository,
        cutters: CutterRepository,
        cutter_operators: CutterOperatorRepository,
        die_cut_operators: DieCutterOperatorRepository,
        films: FilmRepository,
    ) -> None:
        self._printers = printers
        self._press_operators = press_operators
        self._laminators = laminators
        self._laminator_operators = laminator_operators
        self._cutters = cutters
        self._cutter_operators = cutter_operators
        self._die_cut_operators = die_cut_operators
        self._films = films

    def create(self, operation: object, print_run: PrintRun) -> PricingStrategy:
        """Builds the pricing strategy for one run operation.

        :raises KeyError: if a catalog id from the operation is missing.
        :raises TypeError: if the operation type is not supported.
        """
        if isinstance(operation, Print):
            return self._print_pricing(operation, print_run)
        if isinstance(operation, Laminate):
            return self._laminate_pricing(operation, print_run)
        if isinstance(operation, Cut):
            return self._cut_pricing(operation, print_run)
        if isinstance(operation, DieCut):
            return self._die_cut_pricing(operation, print_run)
        raise TypeError(
            f"Unsupported run operation type: {type(operation).__name__}",
        )

    def _print_pricing(self, operation: Print, print_run: PrintRun) -> PrintPricing:
        return PrintPricing(
            printer=self._printers.take(operation.printer_id),
            operator=self._press_operators.take(operation.operator_id),
            chroma=operation.chroma,
            print_run=print_run,
        )

    def _laminate_pricing(
        self,
        operation: Laminate,
        print_run: PrintRun,
    ) -> LaminatePricing:
        return LaminatePricing(
            laminator=self._laminators.take(operation.laminator_id),
            operator=self._laminator_operators.take(operation.operator_id),
            lamination=operation.lamination,
            film=self._films.take(operation.film_id),
            print_run=print_run,
        )

    def _cut_pricing(self, operation: Cut, print_run: PrintRun) -> CutPricing:
        return CutPricing(
            cutter=self._cutters.take(operation.cutter_id),
            operator=self._cutter_operators.take(operation.operator_id),
            print_run=print_run,
        )

    def _die_cut_pricing(
        self,
        operation: DieCut,
        print_run: PrintRun,
    ) -> DieCutPricing:
        return DieCutPricing(
            operator=self._die_cut_operators.take(operation.operator_id),
            print_run=print_run,
        )
