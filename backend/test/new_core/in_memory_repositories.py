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
from backend.new_core.materials.paper import Paper
from backend.new_core.materials.sheet import Sheet, SheetID
from backend.new_core.values.money import Money
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.repository import OrderIdOccupied, OrderNotFound
from backend.new_core.personal.cutter_operator import CutterOperator, CutterOperatorID
from backend.new_core.personal.cutter_operator_repository import CutterOperatorIdOccupied
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
from backend.new_core.personal.press_operator import PressOperator, PressOperatorID
from backend.new_core.personal.press_operator_repository import PressOperatorIdOccupied
from backend.new_core.print_run.print_run import PrintRun, PrintRunID
from backend.new_core.reference.reference import Reference

T = TypeVar("T")


@dataclass
class InMemoryOrderRepository:
    """Stores orders in a dict."""

    orders: dict[OrderID, Order] = field(default_factory=dict)
    _next_id: int = 0

    def take(self, order_id: OrderID) -> Order:
        try:
            return self.orders[order_id]
        except KeyError as exc:
            raise OrderNotFound("take", order_id) from exc

    def generate_id(self) -> OrderID:
        order_id = OrderID(self._next_id)
        self._next_id += 1
        return order_id

    def save(self, order: Order) -> None:
        if order.id in self.orders:
            raise OrderIdOccupied("save", order.id)
        self.orders[order.id] = order

    def replace(self, order: Order) -> None:
        if order.id not in self.orders:
            raise OrderNotFound("replace", order.id)
        self.orders[order.id] = order

    def take_latest(self, limit: int) -> tuple[Order, ...]:
        if limit <= 0:
            return ()
        ids = sorted(self.orders, key=lambda order_id: order_id.value, reverse=True)
        return tuple(self.orders[order_id] for order_id in ids[:limit])


@dataclass
class InMemoryPrintRunRepository:
    """Stores print runs grouped by order id."""

    by_order: dict[OrderID, tuple[PrintRun, ...]] = field(default_factory=dict)
    _next_id_by_order: dict[OrderID, int] = field(default_factory=dict)

    def take_all_for_order(self, order_id: OrderID) -> tuple[PrintRun, ...]:
        return self.by_order.get(order_id, ())

    def generate_id(self, order_id: OrderID) -> PrintRunID:
        nxt = self._next_id_by_order.get(order_id, 0)
        self._next_id_by_order[order_id] = nxt + 1
        return PrintRunID(nxt)

    def save_all_for_order(
        self,
        order_id: OrderID,
        runs: tuple[PrintRun, ...],
    ) -> None:
        for run in runs:
            if run.for_order != order_id:
                raise ValueError(
                    f"run {run.id.value} for_order {run.for_order.value} "
                    f"!= {order_id.value}",
                )
        self.by_order[order_id] = runs


@dataclass
class InMemoryUnitOfWork:
    """Snapshot rollback for in-memory order and print-run stores."""

    orders: InMemoryOrderRepository = field(default_factory=InMemoryOrderRepository)
    print_runs: InMemoryPrintRunRepository = field(
        default_factory=InMemoryPrintRunRepository,
    )

    def transaction(self, work: Callable[[], T]) -> T:
        orders_snapshot = dict(self.orders.orders)
        runs_snapshot = {k: v for k, v in self.print_runs.by_order.items()}
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
    items: dict[FilmID, Film] = field(default_factory=dict)
    _next_id: int = 1

    def take(self, film_id: FilmID) -> Film:
        return self.items[film_id]

    def take_all(self) -> tuple[Film, ...]:
        return tuple(
            self.items[film_id]
            for film_id in sorted(self.items, key=lambda item: item.value)
        )

    def add(self, name: str, price: Money, density: int) -> FilmID:
        film_id = FilmID(self._next_id)
        self._next_id += 1
        self.items[film_id] = Film(
            id=film_id,
            name=name,
            price=price,
            density=density,
        )
        return film_id

    def replace(self, film: Film) -> None:
        if film.id not in self.items:
            raise KeyError(film.id)
        self.items[film.id] = film

    def delete(self, film_id: FilmID) -> None:
        del self.items[film_id]


@dataclass
class InMemorySheetRepository:
    items: dict[SheetID, Sheet] = field(default_factory=dict)
    _next_id: int = 1

    def take(self, sheet_id: SheetID) -> Sheet:
        return self.items[sheet_id]

    def take_all(self) -> tuple[Sheet, ...]:
        return tuple(
            self.items[sheet_id]
            for sheet_id in sorted(self.items, key=lambda item: item.value)
        )

    def add(self, paper: Paper, format: Format) -> SheetID:
        sheet_id = SheetID(self._next_id)
        self._next_id += 1
        self.items[sheet_id] = Sheet(id=sheet_id, paper=paper, format=format)
        return sheet_id

    def replace(self, sheet: Sheet) -> None:
        if sheet.id not in self.items:
            raise KeyError(sheet.id)
        self.items[sheet.id] = sheet

    def delete(self, sheet_id: SheetID) -> None:
        del self.items[sheet_id]


@dataclass
class InMemoryPrinterRepository:
    items: dict[PrinterID, Printer] = field(default_factory=dict)

    def take(self, printer_id: PrinterID) -> Printer:
        return self.items[printer_id]

    def take_all(self) -> tuple[Printer, ...]:
        return tuple(
            self.items[printer_id]
            for printer_id in sorted(self.items, key=lambda item: item.value)
        )

    def save(self, printer: Printer) -> None:
        if printer.id in self.items:
            raise PrinterIdOccupied("save", printer.id)
        self.items[printer.id] = printer

    def delete(self, printer_id: PrinterID) -> None:
        del self.items[printer_id]


@dataclass
class InMemoryPressOperatorRepository:
    items: dict[PressOperatorID, PressOperator] = field(default_factory=dict)

    def take(self, operator_id: PressOperatorID) -> PressOperator:
        return self.items[operator_id]

    def take_all(self) -> tuple[PressOperator, ...]:
        return tuple(
            self.items[operator_id]
            for operator_id in sorted(self.items, key=lambda item: item.value)
        )

    def save(self, operator: PressOperator) -> None:
        if operator.id in self.items:
            raise PressOperatorIdOccupied("save", operator.id)
        self.items[operator.id] = operator

    def delete(self, operator_id: PressOperatorID) -> None:
        del self.items[operator_id]


@dataclass
class InMemoryLaminatorRepository:
    items: dict[LaminatorID, Laminator] = field(default_factory=dict)

    def take(self, laminator_id: LaminatorID) -> Laminator:
        return self.items[laminator_id]

    def take_all(self) -> tuple[Laminator, ...]:
        return tuple(
            self.items[laminator_id]
            for laminator_id in sorted(self.items, key=lambda item: item.value)
        )

    def save(self, laminator: Laminator) -> None:
        if laminator.id in self.items:
            raise LaminatorIdOccupied("save", laminator.id)
        self.items[laminator.id] = laminator

    def delete(self, laminator_id: LaminatorID) -> None:
        del self.items[laminator_id]


@dataclass
class InMemoryLaminatorOperatorRepository:
    items: dict[LaminatorOperatorID, LaminatorOperator] = field(default_factory=dict)

    def take(self, operator_id: LaminatorOperatorID) -> LaminatorOperator:
        return self.items[operator_id]

    def take_all(self) -> tuple[LaminatorOperator, ...]:
        return tuple(
            self.items[operator_id]
            for operator_id in sorted(self.items, key=lambda item: item.value)
        )

    def save(self, operator: LaminatorOperator) -> None:
        if operator.id in self.items:
            raise LaminatorOperatorIdOccupied("save", operator.id)
        self.items[operator.id] = operator

    def delete(self, operator_id: LaminatorOperatorID) -> None:
        del self.items[operator_id]


@dataclass
class InMemoryCutterRepository:
    items: dict[CutterID, Cutter] = field(default_factory=dict)

    def take(self, cutter_id: CutterID) -> Cutter:
        return self.items[cutter_id]

    def take_all(self) -> tuple[Cutter, ...]:
        return tuple(
            self.items[cutter_id]
            for cutter_id in sorted(self.items, key=lambda item: item.value)
        )

    def save(self, cutter: Cutter) -> None:
        if cutter.id in self.items:
            raise CutterIdOccupied("save", cutter.id)
        self.items[cutter.id] = cutter

    def delete(self, cutter_id: CutterID) -> None:
        del self.items[cutter_id]


@dataclass
class InMemoryCutterOperatorRepository:
    items: dict[CutterOperatorID, CutterOperator] = field(default_factory=dict)

    def take(self, operator_id: CutterOperatorID) -> CutterOperator:
        return self.items[operator_id]

    def take_all(self) -> tuple[CutterOperator, ...]:
        return tuple(
            self.items[operator_id]
            for operator_id in sorted(self.items, key=lambda item: item.value)
        )

    def save(self, operator: CutterOperator) -> None:
        if operator.id in self.items:
            raise CutterOperatorIdOccupied("save", operator.id)
        self.items[operator.id] = operator

    def delete(self, operator_id: CutterOperatorID) -> None:
        del self.items[operator_id]


@dataclass
class InMemoryDieCutterOperatorRepository:
    items: dict[DieCutterOperatorID, DieCutterOperator] = field(
        default_factory=dict,
    )

    def take(self, operator_id: DieCutterOperatorID) -> DieCutterOperator:
        return self.items[operator_id]

    def take_all(self) -> tuple[DieCutterOperator, ...]:
        return tuple(
            self.items[operator_id]
            for operator_id in sorted(self.items, key=lambda item: item.value)
        )

    def save(self, operator: DieCutterOperator) -> None:
        if operator.id in self.items:
            raise DieCutterOperatorIdOccupied("save", operator.id)
        self.items[operator.id] = operator

    def delete(self, operator_id: DieCutterOperatorID) -> None:
        del self.items[operator_id]


@dataclass
class InMemoryReferenceRepository:
    """Stores references in insertion order."""

    rows: list[Reference] = field(default_factory=list)

    def take_all(self) -> tuple[Reference, ...]:
        return tuple(self.rows)

    def save(self, reference: Reference) -> None:
        self.rows.append(reference)
