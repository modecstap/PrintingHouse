import re
from decimal import Decimal

import pytest

from backend.core.accountant.money import Money
from backend.new_core import (
    Block,
    Cutter,
    Imposition,
    InvalidInput,
    Order,
    Paper,
    PrintRun,
    Product,
    Sheet,
)
from backend.test.new_core.test_print_run import build_worked_run

_ZERO_CELL = (
    "imposition: сторона ячейки равна 0, "
    "ширина ячейки=0 мм, высота ячейки=10 мм"
)


def _sheet(width: int, height: int) -> Sheet:
    return Sheet(
        paper=Paper(density=0, name="sheet", price_per_kilo=Money(Decimal(0))),
        height=height,
        width=width,
    )


def _rejects(message: str, call) -> None:
    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        call()


def test_cost_report_is_rejected_when_nothing_fits():
    """A press sheet that fits nothing has count 0 and cuts 4, and both run methods reject it."""
    run, _, _, _ = build_worked_run(
        target_width=100,
        target_height=100,
        press_width=50,
        press_height=50,
        required_count=10,
    )
    message = "imposition: на печатный лист влезает 0 целевых листов"

    assert run.imposition.count() == 0
    assert run.imposition.cuts() == 4
    _rejects(message, run.production_count)
    _rejects(message, lambda: run.cost_report(()))


def test_cost_report_is_rejected_when_the_cell_side_is_zero():
    """A target of 0 by 10 makes production count and the cost report reject the zero cell."""
    run, _, _, _ = build_worked_run(target_width=0, target_height=10)

    _rejects(_ZERO_CELL, run.production_count)
    _rejects(_ZERO_CELL, lambda: run.cost_report(()))


def test_cost_report_is_rejected_when_density_is_zero():
    """Press paper density 0 rejects the cost report."""
    run, printing, laminate, cut = build_worked_run(press_density=0)

    _rejects(
        "paper: плотность равна 0",
        lambda: run.cost_report((printing, laminate, cut)),
    )


def test_cost_report_is_rejected_when_the_stack_is_zero():
    """A passed cut with stack height 0 rejects the cost report."""
    run, _, _, cut = build_worked_run(max_stack=0)

    _rejects(
        "cut: листов в стопе 0, высота стопы=0 мм, плотность=100",
        lambda: run.cost_report((cut,)),
    )


@pytest.mark.parametrize(
    ("message", "build"),
    [
        pytest.param(
            "sheet: высота меньше 0, высота=-1 мм",
            lambda: Sheet(
                paper=Paper(
                    density=0,
                    name="sheet",
                    price_per_kilo=Money(Decimal(0)),
                ),
                height=-1,
                width=1,
            ),
            id="height",
        ),
        pytest.param(
            "sheet: ширина меньше 0, ширина=-1 мм",
            lambda: Sheet(
                paper=Paper(
                    density=0,
                    name="sheet",
                    price_per_kilo=Money(Decimal(0)),
                ),
                height=1,
                width=-1,
            ),
            id="width",
        ),
        pytest.param(
            "imposition: вылеты меньше 0, вылеты=-1 мм",
            lambda: Imposition(
                target=_sheet(10, 10),
                press_sheet=_sheet(30, 40),
                bleeds=-1,
                spacing=0,
            ),
            id="bleeds",
        ),
        pytest.param(
            "imposition: поля меньше 0, поля=-1 мм",
            lambda: Imposition(
                target=_sheet(10, 10),
                press_sheet=_sheet(30, 40),
                bleeds=0,
                spacing=-1,
            ),
            id="spacing",
        ),
        pytest.param(
            "order: количество меньше 0, количество=-1",
            lambda: Order(
                id=1,
                product=Product(blocks=(), operations=()),
                count=-1,
            ),
            id="order count",
        ),
        pytest.param(
            "block: количество меньше 0, количество=-1",
            lambda: Block(sheet=_sheet(1, 1), count=-1),
            id="block count",
        ),
        pytest.param(
            "print_run: необходимое количество меньше 0, количество=-1",
            lambda: PrintRun(
                id=1,
                block=Block(sheet=_sheet(1, 1), count=0),
                required_count=-1,
                imposition=Imposition(
                    target=_sheet(100, 100),
                    press_sheet=_sheet(200, 300),
                    bleeds=0,
                    spacing=0,
                ),
            ),
            id="required count",
        ),
        pytest.param(
            "cutter: высота стопы меньше 0, высота=-1 мм",
            lambda: Cutter(id=1, max_stack=-1),
            id="stack",
        ),
    ],
)
def test_negative_measure_is_rejected(message: str, build):
    """One negative measure is rejected in its constructor with that text."""
    _rejects(message, build)
