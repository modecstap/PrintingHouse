"""Use cases that quote, save, list, and price orders."""

from __future__ import annotations

from dataclasses import replace

from backend.new_core.accountant.accountant import Accountant
from backend.new_core.accountant.order_report import OrderReport
from backend.new_core.accountant.pricing.cut_pricing import CutPricing
from backend.new_core.accountant.pricing.die_cut_pricing import DieCutPricing
from backend.new_core.accountant.pricing.laminate_pricing import LaminatePricing
from backend.new_core.accountant.pricing.print_pricing import PrintPricing
from backend.new_core.accountant.pricing_strategy import PricingStrategy
from backend.new_core.accountant.run_estimate import RunEstimate
from backend.new_core.equipment.cutter_repository import CutterRepository
from backend.new_core.materials.film_repository import FilmRepository
from backend.new_core.materials.sheet_repository import SheetRepository
from backend.new_core.part import Part
from backend.new_core.equipment.laminator_repository import LaminatorRepository
from backend.new_core.equipment.printer_repository import PrinterRepository
from backend.new_core.operations.cut.cut import Cut
from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.operations.laminate.laminate import Laminate
from backend.new_core.operations.print.print import Print
from backend.new_core.order.factory import OrderFactory
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.product import Product
from backend.new_core.order.repository import OrderIdOccupied
from backend.new_core.application_services.unit_of_work import OrderUnitOfWork
from backend.new_core.personal.cutter_operator_repository import CutterOperatorRepository
from backend.new_core.personal.die_cutter_operator_repository import (
    DieCutterOperatorRepository,
)
from backend.new_core.personal.laminator_operator_repository import (
    LaminatorOperatorRepository,
)
from backend.new_core.personal.press_operator_repository import PressOperatorRepository
from backend.new_core.print_run.factory import PrintRunFactory
from backend.new_core.print_run.print_run import PrintRun

_MAX_ORDER_ID_ATTEMPTS = 3


class OrderIdAllocationFailed(Exception):
    """Reports that save exhausted occupied-id retries."""

    def __init__(self, last_occupied: OrderID) -> None:
        super().__init__(
            f"save: не удалось выделить id заказа за {_MAX_ORDER_ID_ATTEMPTS} "
            f"попытки, id={last_occupied.value}",
        )
        self.last_occupied = last_occupied


def build_run_estimate(
    run: PrintRun,
    printers: PrinterRepository,
    press_operators: PressOperatorRepository,
    laminators: LaminatorRepository,
    laminator_operators: LaminatorOperatorRepository,
    cutters: CutterRepository,
    cutter_operators: CutterOperatorRepository,
    die_cut_operators: DieCutterOperatorRepository,
    films: FilmRepository,
) -> RunEstimate:
    """Turns run operations into one run estimate.

    :param run:
    :param printers:
    :param press_operators:
    :param laminators:
    :param laminator_operators:
    :param cutters:
    :param cutter_operators:
    :param die_cut_operators:
    :param films:

    :raises KeyError: if a catalog id from an operation is missing.
    :raises TypeError: if an operation type is not supported.

    :return: pricing strategies bound to this run.
    """
    strategies: list[PricingStrategy] = []
    operations = run.block.operations
    for operation in operations:
        if isinstance(operation, Print):
            strategies.append(
                PrintPricing(
                    printer=printers.take(operation.printer_id),
                    operator=press_operators.take(operation.operator_id),
                    chroma=operation.chroma,
                    print_run=run,
                ),
            )
        elif isinstance(operation, Laminate):
            strategies.append(
                LaminatePricing(
                    laminator=laminators.take(operation.laminator_id),
                    operator=laminator_operators.take(
                        operation.operator_id,
                    ),
                    lamination=operation.lamination,
                    film=films.take(operation.film_id),
                    print_run=run,
                ),
            )
        elif isinstance(operation, Cut):
            strategies.append(
                CutPricing(
                    cutter=cutters.take(operation.cutter_id),
                    operator=cutter_operators.take(operation.operator_id),
                    print_run=run,
                ),
            )
        elif isinstance(operation, DieCut):
            strategies.append(
                DieCutPricing(
                    operator=die_cut_operators.take(operation.operator_id),
                    print_run=run,
                ),
            )
        else:
            raise TypeError(
                f"Unsupported run operation type: {type(operation).__name__}",
            )
    return RunEstimate.create(strategies, run=run)


class OrderService:
    """Quotes, saves, lists, and builds price reports for orders."""

    def __init__(
        self,
        uow: OrderUnitOfWork,
        printers: PrinterRepository,
        press_operators: PressOperatorRepository,
        laminators: LaminatorRepository,
        laminator_operators: LaminatorOperatorRepository,
        cutters: CutterRepository,
        cutter_operators: CutterOperatorRepository,
        die_cut_operators: DieCutterOperatorRepository,
        films: FilmRepository,
        sheets: SheetRepository,
    ) -> None:
        """Remembers the unit of work and catalogs.

        :param uow:
        :param printers:
        :param press_operators:
        :param laminators:
        :param laminator_operators:
        :param cutters:
        :param cutter_operators:
        :param die_cut_operators:
        :param films:
        :param sheets:
        """
        self._uow = uow
        self._printers = printers
        self._press_operators = press_operators
        self._laminators = laminators
        self._laminator_operators = laminator_operators
        self._cutters = cutters
        self._cutter_operators = cutter_operators
        self._die_cut_operators = die_cut_operators
        self._films = films
        self._sheets = sheets
        self._order_factory = OrderFactory(uow.orders)
        self._print_run_factory = PrintRunFactory(uow.print_runs)

    def get_orders(self, limit: int) -> tuple[Order, ...]:
        """Returns the latest orders by id.

        :param limit:

        :return: orders from :meth:`OrderRepository.take_latest`.
        """
        return self._uow.orders.take_latest(limit)

    def get_order(self, order_id: OrderID) -> Order:
        """Returns the order with this id.

        :param order_id:

        :raises OrderNotFound: if the order does not exist.

        :return: the order from :meth:`OrderRepository.take`.
        """
        return self._uow.orders.take(order_id)

    def order_report(self, order_id: OrderID) -> OrderReport:
        """Prices the order after tax compensation.

        :param order_id:

        :raises OrderNotFound: if the order does not exist.
        :raises KeyError: if a catalog sheet or film id is missing.

        :return: the report from :meth:`Accountant.order_report`.
        """
        order = self._uow.orders.take(order_id)
        runs = self._uow.print_runs.take_all_for_order(order_id)
        estimates = tuple(
            self._run_estimate(self._rehydrate_run(run)) for run in runs
        )
        return Accountant().order_report(order, estimates)

    def quote(self, product: Product, count: int) -> OrderReport:
        """Prices the product without persisting an order.

        :param product:
        :param count:

        :raises KeyError: if a catalog id is missing.
        :raises TypeError: if an operation type is not supported.
        :raises InvalidInput: if the product or run data is invalid.

        :return: the report from :meth:`Accountant.order_report`.
        """
        order, runs = self._assemble(product, count)
        estimates = tuple(self._run_estimate(run) for run in runs)
        return Accountant().order_report(order, estimates)

    def save(self, product: Product, count: int) -> OrderID:
        """Persists the order and one print run per block.

        :param product:
        :param count:

        :raises OrderIdAllocationFailed: after three occupied order ids.
        :raises InvalidInput: if the product or run data is invalid.

        :return: the stored order id.
        """
        last_occupied: OrderIdOccupied | None = None
        for _ in range(_MAX_ORDER_ID_ATTEMPTS):
            try:
                def work() -> OrderID:
                    order, runs = self._assemble(product, count)
                    self._uow.orders.save(order)
                    self._uow.print_runs.save_all_for_order(order.id, runs)
                    return order.id

                return self._uow.transaction(work)
            except OrderIdOccupied as exc:
                last_occupied = exc
        if last_occupied is None:
            raise RuntimeError("save exhausted retries without OrderIdOccupied")
        raise OrderIdAllocationFailed(last_occupied.order_id) from last_occupied

    def replace(self, order_id: OrderID, product: Product, count: int) -> OrderID:
        """Replaces an existing order and its print runs.

        :param order_id:
        :param product:
        :param count:

        :raises OrderNotFound: if the order does not exist.
        :raises KeyError: if a catalog id is missing.
        :raises TypeError: if an operation type is not supported.
        :raises InvalidInput: if the product or run data is invalid.

        :return: the same order id.
        """

        def work() -> OrderID:
            existing = self._uow.orders.take(order_id)
            hydrated = self._hydrate_product(product)
            order = Order(
                id=order_id,
                product=hydrated,
                count=count,
                description="",
                created_at=existing.created_at,
            )
            runs = tuple(
                self._print_run_factory.create(
                    for_order=order_id,
                    block=block,
                    required_count=count * block.count,
                )
                for block in hydrated.blocks
            )
            self._uow.orders.replace(order)
            self._uow.print_runs.save_all_for_order(order_id, runs)
            return order_id

        return self._uow.transaction(work)

    def _run_estimate(self, run: PrintRun) -> RunEstimate:
        """Turns run operations into one run estimate.

        :param run:

        :raises KeyError: if a catalog id from an operation is missing.
        :raises TypeError: if an operation type is not supported.

        :return: pricing strategies bound to this run.
        """
        return build_run_estimate(
            run,
            self._printers,
            self._press_operators,
            self._laminators,
            self._laminator_operators,
            self._cutters,
            self._cutter_operators,
            self._die_cut_operators,
            self._films,
        )

    def _assemble(
        self,
        product: Product,
        count: int,
    ) -> tuple[Order, tuple[PrintRun, ...]]:
        hydrated = self._hydrate_product(product)
        order = self._order_factory.create(hydrated, count)
        runs = tuple(
            self._print_run_factory.create(
                for_order=order.id,
                block=block,
                required_count=order.count * block.count,
            )
            for block in hydrated.blocks
        )
        return order, runs

    def _hydrate_product(self, product: Product) -> Product:
        """Loads catalog sheet and film rows referenced by the product.

        :param product:

        :raises KeyError: if a referenced sheet or film id is missing.

        :return: a product whose blocks use current catalog ``press_sheet``
        values and whose laminate operations reference known film ids.
        """
        return replace(
            product,
            blocks=tuple(self._hydrate_part(block) for block in product.blocks),
        )

    def _hydrate_part(self, block: Part) -> Part:
        """Hydrates imposition and validates laminate film ids for one block.

        :param block:

        :raises KeyError: if a referenced sheet or film id is missing.

        :return: the block with ``press_sheet`` loaded from the catalog.
        """
        imposition = block.imposition
        sheet = self._sheets.take(imposition.sheet_id)
        hydrated_imposition = replace(imposition, press_sheet=sheet)
        for operation in block.operations:
            if isinstance(operation, Laminate):
                self._films.take(operation.film_id)
        return replace(block, imposition=hydrated_imposition)

    def _rehydrate_run(self, run: PrintRun) -> PrintRun:
        """Rebuilds a stored run with catalog sheet and film rows.

        :param run:

        :raises KeyError: if a referenced sheet or film id is missing.

        :return: a run whose block matches the catalog at report time.
        """
        return PrintRun(
            id=run.id,
            for_order=run.for_order,
            block=self._hydrate_part(run.block),
            required_count=run.required_count,
        )
