"""In-memory repository stubs for new_core behavior tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.new_core.equipment.laminator import Laminator, LaminatorID
from backend.new_core.equipment.printer import Printer, PrinterID
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.repository import OrderNotFound
from backend.new_core.personal.cutter_operator import CutterOperator, CutterOperatorID
from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)
from backend.new_core.personal.press_operator import PressOperator, PressOperatorID
from backend.new_core.print_run.print_run import PrintRun


@dataclass
class InMemoryOrderRepository:
    """Stores orders in a dict."""

    orders: dict[OrderID, Order] = field(default_factory=dict)

    def take(self, order_id: OrderID) -> Order:
        try:
            return self.orders[order_id]
        except KeyError as exc:
            raise OrderNotFound("take", order_id) from exc


@dataclass
class InMemoryPrintRunRepository:
    """Stores print runs grouped by order id."""

    by_order: dict[OrderID, tuple[PrintRun, ...]] = field(default_factory=dict)

    def take_all_for_order(self, order_id: OrderID) -> tuple[PrintRun, ...]:
        return self.by_order.get(order_id, ())


@dataclass
class InMemoryPrinterRepository:
    items: dict[PrinterID, Printer] = field(default_factory=dict)

    def take(self, printer_id: PrinterID) -> Printer:
        return self.items[printer_id]


@dataclass
class InMemoryPressOperatorRepository:
    items: dict[PressOperatorID, PressOperator] = field(default_factory=dict)

    def take(self, operator_id: PressOperatorID) -> PressOperator:
        return self.items[operator_id]


@dataclass
class InMemoryLaminatorRepository:
    items: dict[LaminatorID, Laminator] = field(default_factory=dict)

    def take(self, laminator_id: LaminatorID) -> Laminator:
        return self.items[laminator_id]


@dataclass
class InMemoryLaminatorOperatorRepository:
    items: dict[LaminatorOperatorID, LaminatorOperator] = field(default_factory=dict)

    def take(self, operator_id: LaminatorOperatorID) -> LaminatorOperator:
        return self.items[operator_id]


@dataclass
class InMemoryCutterOperatorRepository:
    items: dict[CutterOperatorID, CutterOperator] = field(default_factory=dict)

    def take(self, operator_id: CutterOperatorID) -> CutterOperator:
        return self.items[operator_id]


@dataclass
class InMemoryDieCutterOperatorRepository:
    items: dict[DieCutterOperatorID, DieCutterOperator] = field(
        default_factory=dict,
    )

    def take(self, operator_id: DieCutterOperatorID) -> DieCutterOperator:
        return self.items[operator_id]
