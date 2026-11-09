"""Use cases that price a stored order."""

from __future__ import annotations

from backend.new_core.accountant.accountant import Accountant
from backend.new_core.accountant.order_report import OrderReport
from backend.new_core.accountant.pricing.cut_pricing import CutPricing
from backend.new_core.accountant.pricing.die_cut_pricing import DieCutPricing
from backend.new_core.accountant.pricing.laminate_pricing import LaminatePricing
from backend.new_core.accountant.pricing.print_pricing import PrintPricing
from backend.new_core.accountant.pricing_strategy import PricingStrategy
from backend.new_core.accountant.run_estimate import RunEstimate
from backend.new_core.equipment.laminator_repository import LaminatorRepository
from backend.new_core.equipment.printer_repository import PrinterRepository
from backend.new_core.operations.cut.cut import Cut
from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.operations.laminate.laminate import Laminate
from backend.new_core.operations.print.print import Print
from backend.new_core.order.order import OrderID
from backend.new_core.order.repository import OrderRepository
from backend.new_core.personal.cutter_operator_repository import CutterOperatorRepository
from backend.new_core.personal.die_cutter_operator_repository import (
    DieCutterOperatorRepository,
)
from backend.new_core.personal.laminator_operator_repository import (
    LaminatorOperatorRepository,
)
from backend.new_core.personal.press_operator_repository import PressOperatorRepository
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.print_run.repository import PrintRunRepository


class OrderReportService:
    """Builds an order price report from stored runs and catalogs."""

    def __init__(
        self,
        orders: OrderRepository,
        print_runs: PrintRunRepository,
        printers: PrinterRepository,
        press_operators: PressOperatorRepository,
        laminators: LaminatorRepository,
        laminator_operators: LaminatorOperatorRepository,
        cutter_operators: CutterOperatorRepository,
        die_cut_operators: DieCutterOperatorRepository,
    ) -> None:
        """Remembers the repositories used to load order data and catalogs.

        :param orders:
        :param print_runs:
        :param printers:
        :param press_operators:
        :param laminators:
        :param laminator_operators:
        :param cutter_operators:
        :param die_cut_operators:
        """
        self._orders = orders
        self._print_runs = print_runs
        self._printers = printers
        self._press_operators = press_operators
        self._laminators = laminators
        self._laminator_operators = laminator_operators
        self._cutter_operators = cutter_operators
        self._die_cut_operators = die_cut_operators

    def order_report(self, order_id: OrderID) -> OrderReport:
        """Prices the order after tax compensation.

        :param order_id:

        :raises OrderNotFound: if the order does not exist.

        :return: the report from :meth:`Accountant.order_report`.
        """
        order = self._orders.take(order_id)
        runs = self._print_runs.take_all_for_order(order_id)
        estimates = tuple(self._run_estimate(run) for run in runs)
        return Accountant().order_report(order, estimates)

    def _run_estimate(self, run: PrintRun) -> RunEstimate:
        """Turns run operations into one run estimate.

        :param run:

        :raises KeyError: if a catalog id from an operation is missing.
        :raises TypeError: if an operation type is not supported.

        :return: pricing strategies bound to this run.
        """
        strategies: list[PricingStrategy] = []
        for operation in run.operations:
            if isinstance(operation, Print):
                strategies.append(
                    PrintPricing(
                        printer=self._printers.take(operation.printer_id),
                        operator=self._press_operators.take(operation.operator_id),
                        chroma=operation.chroma,
                        paper=operation.paper,
                        print_run=run,
                    ),
                )
            elif isinstance(operation, Laminate):
                strategies.append(
                    LaminatePricing(
                        laminator=self._laminators.take(operation.laminator_id),
                        operator=self._laminator_operators.take(
                            operation.operator_id,
                        ),
                        lamination=operation.lamination,
                        film=operation.film,
                        print_run=run,
                    ),
                )
            elif isinstance(operation, Cut):
                strategies.append(
                    CutPricing(
                        cutter=operation.cutter,
                        operator=self._cutter_operators.take(operation.operator_id),
                        print_run=run,
                    ),
                )
            elif isinstance(operation, DieCut):
                strategies.append(
                    DieCutPricing(
                        operator=self._die_cut_operators.take(operation.operator_id),
                        print_run=run,
                    ),
                )
            else:
                raise TypeError(
                    f"Unsupported run operation type: {type(operation).__name__}",
                )
        return RunEstimate.create(strategies, run=run)
