"""Catalog factories assign ids from the repository."""

from decimal import Decimal

from backend.new_core.equipment.factory import PrinterFactory
from backend.new_core.equipment.printer import PrinterID, PrinterPrices
from backend.new_core.personal.factory import PressOperatorFactory
from backend.new_core.personal.press_operator import PressOperatorID
from backend.new_core.values.money import Money
from backend.test.new_core.in_memory_repositories import (
    InMemoryPressOperatorRepository,
    InMemoryPrinterRepository,
)


def test_printer_factory_assigns_sequential_ids() -> None:
    repo = InMemoryPrinterRepository()
    factory = PrinterFactory(repo)
    money = Money(Decimal("1"))

    prices = PrinterPrices(
        startup=money,
        cyan=money,
        magenta=money,
        yellow=money,
        black=money,
    )
    first = factory.create(name="P1", spacing=3, prices=prices)
    second = factory.create(name="P2", spacing=3, prices=prices)

    assert first.id == PrinterID(0)
    assert second.id == PrinterID(1)


def test_press_operator_factory_assigns_id_from_repo() -> None:
    repo = InMemoryPressOperatorRepository()
    factory = PressOperatorFactory(repo)

    operator = factory.create(
        name="Op",
        salary_by_operation=Money(Decimal("100")),
    )

    assert operator.id == PressOperatorID(0)