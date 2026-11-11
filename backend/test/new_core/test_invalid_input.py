"""Constructors reject a measure that is below its allowed minimum."""

import re
from decimal import Decimal

import pytest

from backend.new_core.equipment.cutter import CutterID
from backend.new_core.equipment.laminator import LaminatorID
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.materials.film import FilmID
from backend.new_core.materials.paper_type import PaperType
from backend.new_core.materials.sheet import SheetID
from backend.new_core.personal.cutter_operator import CutterOperatorID
from backend.new_core.personal.die_cutter_operator import DieCutterOperatorID
from backend.new_core.personal.laminator_operator import LaminatorOperatorID
from backend.new_core.personal.press_operator import PressOperatorID
from backend.new_core.order.order import OrderID
from backend.new_core.print_run.print_run import PrintRunID
from backend.test.storage.helpers import TEST_ORDER_CREATED_AT
from backend.new_core.values.money import Money
from backend.new_core import (
    Part,
    Cutter,
    Format,
    Imposition,
    InvalidInput,
    Order,
    Paper,
    Percent,
    PrintRun,
    Product,
    Sheet,
)
from backend.test.new_core.test_print_run import build_worked_run

_ZERO_CELL = (
    "Imposition: сторона ячейки равна 0, "
    "ширина ячейки=0 мм, высота ячейки=10 мм"
)


def _sheet(width: int, height: int, *, sheet_id: SheetID | None = None) -> Sheet:
    return Sheet(
        id=sheet_id or SheetID(1),
        paper=Paper(
            density=60,
            thickness=Decimal(1),
            type=PaperType("sheet"),
            price_per_kilo=Money(Decimal(0)),
        ),
        format=Format(name="sheet", height=height, width=width),
    )


def _fitting_imposition() -> Imposition:
    press_sheet = _sheet(200, 300)
    return Imposition(
        target=Format(name="t", height=100, width=100),
        sheet_id=press_sheet.id,
        press_sheet=press_sheet,
        bleeds=0,
        spacing=0,
    )


def _block(count: int) -> Part:
    return Part(
        imposition=_fitting_imposition(),
        count=count,
        operations=(),
    )


def _rejects(message: str, call) -> None:
    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        call()


def test_imposition_rejects_count_when_nothing_fits():
    """A 100 by 100 target on a 50 by 50 press sheet is rejected at construction."""
    message = "Imposition: на печатный лист влезает 0 целевых листов"

    def _build() -> None:
        press_sheet = _sheet(50, 50)
        Imposition(
            target=Format(name="t", height=100, width=100),
            sheet_id=press_sheet.id,
            press_sheet=press_sheet,
            bleeds=0,
            spacing=0,
        )

    _rejects(message, _build)


def test_print_run_rejects_a_zero_cell_side():
    """A target of 0 by 10 rejects the run because the cell side is zero."""
    _rejects(
        _ZERO_CELL,
        lambda: build_worked_run(target_width=0, target_height=10),
    )


def test_product_rejects_empty_blocks():
    """A product with no blocks is rejected at construction."""
    _rejects(
        "Product: нет блоков продукта",
        lambda: Product(parts_markup=Percent(0), blocks=(), operations=()),
    )


def test_paper_rejects_a_density_of_zero():
    """A paper density of 0 is rejected."""
    _rejects(
        "Paper: плотность бумаги меньше или равна 0, плотность=0 г/м²",
        lambda: Paper(
            density=0,
            thickness=Decimal(1),
            type=PaperType("press"),
            price_per_kilo=Money(Decimal(1000)),
        ),
    )


def test_paper_accepts_fractional_thickness():
    """A paper thickness of 0.15 mm is accepted."""
    Paper(
        density=60,
        thickness=Decimal("0.15"),
        type=PaperType("press"),
        price_per_kilo=Money(Decimal(1000)),
    )


def test_paper_rejects_thickness_with_more_than_two_decimal_places():
    """More than two fractional digits in thickness is rejected."""
    _rejects(
        "Paper: толщина бумаги имеет более 2 знаков после запятой, "
        "толщина=0.151 мм",
        lambda: Paper(
            density=60,
            thickness=Decimal("0.151"),
            type=PaperType("press"),
            price_per_kilo=Money(Decimal(1000)),
        ),
    )


def test_paper_rejects_a_thickness_of_zero():
    """A paper thickness of 0 is rejected."""
    _rejects(
        "Paper: толщина бумаги меньше или равна 0, толщина=0 мм",
        lambda: Paper(
            density=60,
            thickness=Decimal(0),
            type=PaperType("press"),
            price_per_kilo=Money(Decimal(1000)),
        ),
    )


def test_cutter_rejects_a_stack_height_of_zero():
    """A stack height of 0 is rejected."""
    _rejects(
        "cutter: высота стопы равна 0, высота=0 мм",
        lambda: Cutter(id=CutterID(1), max_stack=0),
    )


@pytest.mark.parametrize(
    ("message", "build"),
    [
        pytest.param(
            "Format: высота меньше 0, высота=-1 мм",
            lambda: Format(name="", height=-1, width=1),
            id="height",
        ),
        pytest.param(
            "Format: ширина меньше 0, ширина=-1 мм",
            lambda: Format(name="", height=1, width=-1),
            id="width",
        ),
        pytest.param(
            "Imposition: вылеты меньше 0, вылеты=-1 мм",
            lambda: Imposition(
                target=Format(name="t", height=10, width=10),
                sheet_id=SheetID(1),
                press_sheet=_sheet(30, 40),
                bleeds=-1,
                spacing=0,
            ),
            id="bleeds",
        ),
        pytest.param(
            "Imposition: поля меньше 0, поля=-1 мм",
            lambda: Imposition(
                target=Format(name="t", height=10, width=10),
                sheet_id=SheetID(1),
                press_sheet=_sheet(30, 40),
                bleeds=0,
                spacing=-1,
            ),
            id="spacing",
        ),
        pytest.param(
            "order: количество меньше 0, количество=-1",
            lambda: Order(
                id=OrderID(1),
                product=Product(
                    parts_markup=Percent(0),
                    blocks=(_block(0),),
                    operations=(),
                ),
                count=-1,
                description="",
                created_at=TEST_ORDER_CREATED_AT,
            ),
            id="order count",
        ),
        pytest.param(
            "Part: количество меньше 0, количество=-1",
            lambda: _block(-1),
            id="block count",
        ),
        pytest.param(
            "print_run: необходимое количество меньше 0, количество=-1",
            lambda: PrintRun(
                id=PrintRunID(1),
                for_order=OrderID(1),
                block=_block(0),
                required_count=-1,
            ),
            id="required count",
        ),
        pytest.param(
            "cutter: высота стопы меньше 0, высота=-1 мм",
            lambda: Cutter(id=CutterID(1), max_stack=-1),
            id="stack",
        ),
    ],
)
def test_negative_measure_is_rejected(message: str, build):
    """One negative measure is rejected in its constructor with that text."""
    _rejects(message, build)


@pytest.mark.parametrize(
    ("message", "build"),
    [
        pytest.param(
            "Paper: плотность бумаги меньше или равна 0, плотность=0 г/м²; "
            "толщина бумаги меньше или равна 0, толщина=0 мм",
            lambda: Paper(
                density=0,
                thickness=Decimal(0),
                type=PaperType("press"),
                price_per_kilo=Money(Decimal(1000)),
            ),
            id="paper",
        ),
        pytest.param(
            "Format: высота меньше 0, высота=-1 мм; ширина меньше 0, ширина=-1 мм",
            lambda: Format(name="", height=-1, width=-1),
            id="format",
        ),
        pytest.param(
            "Imposition: вылеты меньше 0, вылеты=-1 мм; поля меньше 0, поля=-1 мм",
            lambda: Imposition(
                target=Format(name="t", height=10, width=10),
                sheet_id=SheetID(1),
                press_sheet=_sheet(30, 40),
                bleeds=-1,
                spacing=-1,
            ),
            id="imposition",
        ),
    ],
)
def test_every_invalid_field_is_reported(message: str, build):
    """Every invalid field is named in one error."""
    _rejects(message, build)


@pytest.mark.parametrize(
    ("message", "build"),
    [
        pytest.param(
            "order id",
            lambda: OrderID(-1),
            id="order id",
        ),
        pytest.param(
            "print run id",
            lambda: PrintRunID(-1),
            id="print run id",
        ),
        pytest.param(
            "cutter id",
            lambda: CutterID(-1),
            id="cutter id",
        ),
        pytest.param("printer id", lambda: PrinterID(-1), id="printer id"),
        pytest.param("film id", lambda: FilmID(-1), id="film id"),
        pytest.param("sheet id", lambda: SheetID(-1), id="sheet id"),
        pytest.param("laminator id", lambda: LaminatorID(-1), id="laminator id"),
        pytest.param(
            "press operator id",
            lambda: PressOperatorID(-1),
            id="press operator id",
        ),
        pytest.param(
            "laminator operator id",
            lambda: LaminatorOperatorID(-1),
            id="laminator operator id",
        ),
        pytest.param(
            "cutter operator id",
            lambda: CutterOperatorID(-1),
            id="cutter operator id",
        ),
        pytest.param(
            "die cutter operator id",
            lambda: DieCutterOperatorID(-1),
            id="die cutter operator id",
        ),
    ],
)
def test_negative_id_is_rejected(message: str, build):
    """A negative catalog or entity id is rejected at construction."""
    with pytest.raises(InvalidInput, match=message):
        build()
