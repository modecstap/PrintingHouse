"""In-memory repository stubs for new_core behavior tests."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeVar

from backend.new_core.equipment.cutter import Cutter, CutterID
from backend.new_core.equipment.cutter_repository import CutterIdOccupied
from backend.new_core.equipment.laminator import Laminator, LaminatorID
from backend.new_core.equipment.laminator_repository import LaminatorIdOccupied
from backend.new_core.equipment.printer import Printer, PrinterID
from backend.new_core.equipment.printer_repository import PrinterIdOccupied
from backend.new_core.format import Format
from backend.new_core.materials.film import Film, FilmID
from backend.new_core.materials.film_density import FilmDensity
from backend.new_core.materials.paper import Paper
from backend.new_core.materials.sheet import Sheet, SheetID
from backend.new_core.values.money import Money
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.repository import OrderIdOccupied, OrderNotFound
from backend.new_core.personal.cutter_operator import (
    CutterOperator,
    CutterOperatorID,
)
from backend.new_core.personal.cutter_operator_repository import (
    CutterOperatorIdOccupied,
)
from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.new_core.personal.die_cutter_operator_repository import (
    DieCutterOperatorIdOccupied,
)
from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)
from backend.new_core.personal.laminator_operator_repository import (
    LaminatorOperatorIdOccupied,
)
from backend.new_core.personal.press_operator import (
    PressOperator,
    PressOperatorID,
)
from backend.new_core.personal.press_operator_repository import (
    PressOperatorIdOccupied,
)
from backend.new_core.print_run.print_run import (
    PrintRun,
    PrintRunID,
    require_runs_belong_to_order,
)
from backend.new_core.reference.reference import Reference

__all__ = [
    "T",
    "InMemoryOrderRepository",
    "InMemoryPrintRunRepository",
    "InMemoryUnitOfWork",
    "InMemoryFilmRepository",
    "InMemorySheetRepository",
    "InMemoryPrinterRepository",
    "InMemoryPressOperatorRepository",
    "InMemoryLaminatorRepository",
    "InMemoryLaminatorOperatorRepository",
    "InMemoryCutterRepository",
    "InMemoryCutterOperatorRepository",
    "InMemoryDieCutterOperatorRepository",
    "InMemoryReferenceRepository",
]

T = TypeVar("T")


@dataclass
class InMemoryOrderRepository:
    """Stores orders in a dict."""

    orders: dict[OrderID, Order] = field(default_factory=dict)
    _next_id: int = 0

    def take(self, order_id: OrderID) -> Order:
        """Handles take.

        :param order_id: id of the order.

        :raises OrderNotFound: when the operation fails.

        :return: the Order result.
        """
        try:
            return self.orders[order_id]
        except KeyError as exc:
            raise OrderNotFound("take", order_id) from exc

    def generate_id(self) -> OrderID:
        """Handles generate id.

        :return: the OrderID result.
        """
        order_id = OrderID(self._next_id)
        self._next_id += 1
        return order_id

    def save(self, order: Order) -> None:
        """Persists the save.

        :param order: the order.

        :raises OrderIdOccupied: when the operation fails.
        """
        if order.id in self.orders:
            raise OrderIdOccupied("save", order.id)
        self.orders[order.id] = order

    def replace(self, order: Order) -> None:
        """Replaces the replace.

        :param order: the order.

        :raises OrderNotFound: when the operation fails.
        """
        if order.id not in self.orders:
            raise OrderNotFound("replace", order.id)
        self.orders[order.id] = order

    def take_latest(self, limit: int) -> tuple[Order, ...]:
        """Handles take latest.

        :param limit: the limit.

        :return: the tuple[Order, ...] result.
        """
        if limit <= 0:
            return ()
        ids = sorted(
            self.orders,
            key=lambda order_id: order_id.value,
            reverse=True)
        return tuple(self.orders[order_id] for order_id in ids[:limit])


@dataclass
class InMemoryPrintRunRepository:
    """Stores print runs grouped by order id."""

    by_order: dict[OrderID, tuple[PrintRun, ...]] = field(default_factory=dict)
    _next_id_by_order: dict[OrderID, int] = field(default_factory=dict)

    def take_all_for_order(self, order_id: OrderID) -> tuple[PrintRun, ...]:
        """Handles take all for order.

        :param order_id: id of the order.

        :return: the tuple[PrintRun, ...] result.
        """
        return self.by_order.get(order_id, ())

    def generate_id(self, order_id: OrderID) -> PrintRunID:
        """Handles generate id.

        :param order_id: id of the order.

        :return: the PrintRunID result.
        """
        nxt = self._next_id_by_order.get(order_id, 0)
        self._next_id_by_order[order_id] = nxt + 1
        return PrintRunID(nxt)

    def save_all_for_order(
        self,
        order_id: OrderID,
        runs: tuple[PrintRun, ...],
    ) -> None:
        """Persists the all for order.

        :param order_id: id of the order.
        :param runs: the runs.
        """
        require_runs_belong_to_order(order_id, runs)
        self.by_order[order_id] = runs


@dataclass
class InMemoryUnitOfWork:
    """Snapshot rollback for in-memory order and print-run stores."""

    orders: InMemoryOrderRepository = field(
        default_factory=InMemoryOrderRepository)
    print_runs: InMemoryPrintRunRepository = field(
        default_factory=InMemoryPrintRunRepository,
    )

    def transaction(self, work: Callable[[], T]) -> T:
        """Handles transaction.

        :param work: the work.

        :return: the T result.
        """
        orders_snapshot = dict(self.orders.orders)
        runs_snapshot = dict(self.print_runs.by_order)
        try:
            return work()
        except Exception:
            self.orders.orders.clear()
            self.orders.orders.update(orders_snapshot)
            self.print_runs.by_order.clear()
            self.print_runs.by_order.update(runs_snapshot)
            raise


@dataclass
class InMemoryFilmRepository:
    """In Memory Film Repository.
    """
    items: dict[FilmID, Film] = field(default_factory=dict)
    _next_id: int = 1

    def take(self, film_id: FilmID) -> Film:
        """Handles take.

        :param film_id: id of the film.

        :return: the Film result.
        """
        return self.items[film_id]

    def take_all(self) -> tuple[Film, ...]:
        """Handles take all.

        :return: the tuple[Film, ...] result.
        """
        return tuple(
            self.items[film_id]
            for film_id in sorted(self.items, key=lambda item: item.value)
        )

    def add(self, name: str, price: Money, density: int) -> FilmID:
        """Adds a add.

        :param name: the name.
        :param price: the price.
        :param density: the density.

        :return: the FilmID result.
        """
        film_id = FilmID(self._next_id)
        self._next_id += 1
        self.items[film_id] = Film(
            id=film_id,
            name=name,
            price=price,
            density=FilmDensity(density),
        )
        return film_id

    def replace(self, film: Film) -> None:
        """Replaces the replace.

        :param film: the film.

        :raises KeyError: when the operation fails.
        """
        if film.id not in self.items:
            raise KeyError(film.id)
        self.items[film.id] = film

    def delete(self, film_id: FilmID) -> None:
        """Deletes the delete.

        :param film_id: id of the film.
        """
        del self.items[film_id]

    def distinct_film_densities(self) -> tuple[int, ...]:
        """Handles distinct film densities.

        :return: the tuple[int, ...] result.
        """
        values = {film.density.value for film in self.items.values()}
        return tuple(sorted(values))


@dataclass
class InMemorySheetRepository:
    """In Memory Sheet Repository.
    """
    items: dict[SheetID, Sheet] = field(default_factory=dict)
    _next_id: int = 1

    def take(self, sheet_id: SheetID) -> Sheet:
        """Handles take.

        :param sheet_id: id of the sheet.

        :return: the Sheet result.
        """
        return self.items[sheet_id]

    def take_all(self) -> tuple[Sheet, ...]:
        """Handles take all.

        :return: the tuple[Sheet, ...] result.
        """
        return tuple(
            self.items[sheet_id]
            for sheet_id in sorted(self.items, key=lambda item: item.value)
        )

    def add(self, paper: Paper, sheet_format: Format) -> SheetID:
        """Adds a add.

        :param paper: the paper.
        :param sheet_format: the sheet format.

        :return: the SheetID result.
        """
        sheet_id = SheetID(self._next_id)
        self._next_id += 1
        self.items[sheet_id] = Sheet(
            id=sheet_id,
            paper=paper,
            format=sheet_format,
        )
        return sheet_id

    def replace(self, sheet: Sheet) -> None:
        """Replaces the replace.

        :param sheet: the sheet.

        :raises KeyError: when the operation fails.
        """
        if sheet.id not in self.items:
            raise KeyError(sheet.id)
        self.items[sheet.id] = sheet

    def delete(self, sheet_id: SheetID) -> None:
        """Deletes the delete.

        :param sheet_id: id of the sheet.
        """
        del self.items[sheet_id]

    def distinct_paper_types(self) -> tuple[str, ...]:
        """Handles distinct paper types.

        :return: the tuple[str, ...] result.
        """
        values = {sheet.paper.type.value for sheet in self.items.values()}
        return tuple(sorted(values))

    def distinct_paper_densities(self) -> tuple[int, ...]:
        """Handles distinct paper densities.

        :return: the tuple[int, ...] result.
        """
        values = {sheet.paper.density.value for sheet in self.items.values()}
        return tuple(sorted(values))


@dataclass
class InMemoryPrinterRepository:
    """In Memory Printer Repository.
    """
    items: dict[PrinterID, Printer] = field(default_factory=dict)
    _next_id: int = 0

    def take(self, printer_id: PrinterID) -> Printer:
        """Handles take.

        :param printer_id: id of the printer.

        :return: the Printer result.
        """
        return self.items[printer_id]

    def take_all(self) -> tuple[Printer, ...]:
        """Handles take all.

        :return: the tuple[Printer, ...] result.
        """
        return tuple(
            self.items[printer_id]
            for printer_id in sorted(self.items, key=lambda item: item.value)
        )

    def generate_id(self) -> PrinterID:
        """Handles generate id.

        :return: the PrinterID result.
        """
        while True:
            printer_id = PrinterID(self._next_id)
            self._next_id += 1
            if printer_id not in self.items:
                return printer_id

    def save(self, printer: Printer) -> None:
        """Persists the save.

        :param printer: the printer.

        :raises PrinterIdOccupied: when the operation fails.
        """
        if printer.id in self.items:
            raise PrinterIdOccupied("save", printer.id)
        self.items[printer.id] = printer

    def delete(self, printer_id: PrinterID) -> None:
        """Deletes the delete.

        :param printer_id: id of the printer.
        """
        del self.items[printer_id]


@dataclass
class InMemoryPressOperatorRepository:
    """In Memory Press Operator Repository.
    """
    items: dict[PressOperatorID, PressOperator] = field(default_factory=dict)
    _next_id: int = 0

    def take(self, operator_id: PressOperatorID) -> PressOperator:
        """Handles take.

        :param operator_id: id of the operator.

        :return: the PressOperator result.
        """
        return self.items[operator_id]

    def take_all(self) -> tuple[PressOperator, ...]:
        """Handles take all.

        :return: the tuple[PressOperator, ...] result.
        """
        return tuple(
            self.items[operator_id]
            for operator_id in sorted(self.items, key=lambda item: item.value)
        )

    def generate_id(self) -> PressOperatorID:
        """Handles generate id.

        :return: the PressOperatorID result.
        """
        while True:
            operator_id = PressOperatorID(self._next_id)
            self._next_id += 1
            if operator_id not in self.items:
                return operator_id

    def save(self, operator: PressOperator) -> None:
        """Persists the save.

        :param operator: the operator.

        :raises PressOperatorIdOccupied: when the operation fails.
        """
        if operator.id in self.items:
            raise PressOperatorIdOccupied("save", operator.id)
        self.items[operator.id] = operator

    def delete(self, operator_id: PressOperatorID) -> None:
        """Deletes the delete.

        :param operator_id: id of the operator.
        """
        del self.items[operator_id]


@dataclass
class InMemoryLaminatorRepository:
    """In Memory Laminator Repository.
    """
    items: dict[LaminatorID, Laminator] = field(default_factory=dict)
    _next_id: int = 0

    def take(self, laminator_id: LaminatorID) -> Laminator:
        """Handles take.

        :param laminator_id: id of the laminator.

        :return: the Laminator result.
        """
        return self.items[laminator_id]

    def take_all(self) -> tuple[Laminator, ...]:
        """Handles take all.

        :return: the tuple[Laminator, ...] result.
        """
        return tuple(
            self.items[laminator_id]
            for laminator_id in sorted(self.items, key=lambda item: item.value)
        )

    def generate_id(self) -> LaminatorID:
        """Handles generate id.

        :return: the LaminatorID result.
        """
        while True:
            laminator_id = LaminatorID(self._next_id)
            self._next_id += 1
            if laminator_id not in self.items:
                return laminator_id

    def save(self, laminator: Laminator) -> None:
        """Persists the save.

        :param laminator: the laminator.

        :raises LaminatorIdOccupied: when the operation fails.
        """
        if laminator.id in self.items:
            raise LaminatorIdOccupied("save", laminator.id)
        self.items[laminator.id] = laminator

    def delete(self, laminator_id: LaminatorID) -> None:
        """Deletes the delete.

        :param laminator_id: id of the laminator.
        """
        del self.items[laminator_id]


@dataclass
class InMemoryLaminatorOperatorRepository:
    """In Memory Laminator Operator Repository.
    """
    items: dict[LaminatorOperatorID, LaminatorOperator] = field(
        default_factory=dict)
    _next_id: int = 0

    def take(self, operator_id: LaminatorOperatorID) -> LaminatorOperator:
        """Handles take.

        :param operator_id: id of the operator.

        :return: the LaminatorOperator result.
        """
        return self.items[operator_id]

    def take_all(self) -> tuple[LaminatorOperator, ...]:
        """Handles take all.

        :return: the tuple[LaminatorOperator, ...] result.
        """
        return tuple(
            self.items[operator_id]
            for operator_id in sorted(self.items, key=lambda item: item.value)
        )

    def generate_id(self) -> LaminatorOperatorID:
        """Handles generate id.

        :return: the LaminatorOperatorID result.
        """
        while True:
            operator_id = LaminatorOperatorID(self._next_id)
            self._next_id += 1
            if operator_id not in self.items:
                return operator_id

    def save(self, operator: LaminatorOperator) -> None:
        """Persists the save.

        :param operator: the operator.

        :raises LaminatorOperatorIdOccupied: when the operation fails.
        """
        if operator.id in self.items:
            raise LaminatorOperatorIdOccupied("save", operator.id)
        self.items[operator.id] = operator

    def delete(self, operator_id: LaminatorOperatorID) -> None:
        """Deletes the delete.

        :param operator_id: id of the operator.
        """
        del self.items[operator_id]


@dataclass
class InMemoryCutterRepository:
    """In Memory Cutter Repository.
    """
    items: dict[CutterID, Cutter] = field(default_factory=dict)
    _next_id: int = 0

    def take(self, cutter_id: CutterID) -> Cutter:
        """Handles take.

        :param cutter_id: id of the cutter.

        :return: the Cutter result.
        """
        return self.items[cutter_id]

    def take_all(self) -> tuple[Cutter, ...]:
        """Handles take all.

        :return: the tuple[Cutter, ...] result.
        """
        return tuple(
            self.items[cutter_id]
            for cutter_id in sorted(self.items, key=lambda item: item.value)
        )

    def generate_id(self) -> CutterID:
        """Handles generate id.

        :return: the CutterID result.
        """
        while True:
            cutter_id = CutterID(self._next_id)
            self._next_id += 1
            if cutter_id not in self.items:
                return cutter_id

    def save(self, cutter: Cutter) -> None:
        """Persists the save.

        :param cutter: the cutter.

        :raises CutterIdOccupied: when the operation fails.
        """
        if cutter.id in self.items:
            raise CutterIdOccupied("save", cutter.id)
        self.items[cutter.id] = cutter

    def delete(self, cutter_id: CutterID) -> None:
        """Deletes the delete.

        :param cutter_id: id of the cutter.
        """
        del self.items[cutter_id]


@dataclass
class InMemoryCutterOperatorRepository:
    """In Memory Cutter Operator Repository.
    """
    items: dict[CutterOperatorID, CutterOperator] = field(default_factory=dict)
    _next_id: int = 0

    def take(self, operator_id: CutterOperatorID) -> CutterOperator:
        """Handles take.

        :param operator_id: id of the operator.

        :return: the CutterOperator result.
        """
        return self.items[operator_id]

    def take_all(self) -> tuple[CutterOperator, ...]:
        """Handles take all.

        :return: the tuple[CutterOperator, ...] result.
        """
        return tuple(
            self.items[operator_id]
            for operator_id in sorted(self.items, key=lambda item: item.value)
        )

    def generate_id(self) -> CutterOperatorID:
        """Handles generate id.

        :return: the CutterOperatorID result.
        """
        while True:
            operator_id = CutterOperatorID(self._next_id)
            self._next_id += 1
            if operator_id not in self.items:
                return operator_id

    def save(self, operator: CutterOperator) -> None:
        """Persists the save.

        :param operator: the operator.

        :raises CutterOperatorIdOccupied: when the operation fails.
        """
        if operator.id in self.items:
            raise CutterOperatorIdOccupied("save", operator.id)
        self.items[operator.id] = operator

    def delete(self, operator_id: CutterOperatorID) -> None:
        """Deletes the delete.

        :param operator_id: id of the operator.
        """
        del self.items[operator_id]


@dataclass
class InMemoryDieCutterOperatorRepository:
    """In Memory Die Cutter Operator Repository.
    """
    items: dict[DieCutterOperatorID, DieCutterOperator] = field(
        default_factory=dict,
    )
    _next_id: int = 0

    def take(self, operator_id: DieCutterOperatorID) -> DieCutterOperator:
        """Handles take.

        :param operator_id: id of the operator.

        :return: the DieCutterOperator result.
        """
        return self.items[operator_id]

    def take_all(self) -> tuple[DieCutterOperator, ...]:
        """Handles take all.

        :return: the tuple[DieCutterOperator, ...] result.
        """
        return tuple(
            self.items[operator_id]
            for operator_id in sorted(self.items, key=lambda item: item.value)
        )

    def generate_id(self) -> DieCutterOperatorID:
        """Handles generate id.

        :return: the DieCutterOperatorID result.
        """
        while True:
            operator_id = DieCutterOperatorID(self._next_id)
            self._next_id += 1
            if operator_id not in self.items:
                return operator_id

    def save(self, operator: DieCutterOperator) -> None:
        """Persists the save.

        :param operator: the operator.

        :raises DieCutterOperatorIdOccupied: when the operation fails.
        """
        if operator.id in self.items:
            raise DieCutterOperatorIdOccupied("save", operator.id)
        self.items[operator.id] = operator

    def delete(self, operator_id: DieCutterOperatorID) -> None:
        """Deletes the delete.

        :param operator_id: id of the operator.
        """
        del self.items[operator_id]


@dataclass
class InMemoryReferenceRepository:
    """Stores references in insertion order."""

    rows: list[Reference] = field(default_factory=list)

    def take_all(self) -> tuple[Reference, ...]:
        """Handles take all.

        :return: the tuple[Reference, ...] result.
        """
        return tuple(self.rows)

    def save(self, reference: Reference) -> None:
        """Persists the save.

        :param reference: the reference.
        """
        self.rows.append(reference)
