"""Constructors reject a measure that is below its allowed minimum."""

import re
from decimal import Decimal

import pytest

from backend.new_core.equipment.cutter import CutterID
from backend.new_core.equipment.laminator import LaminatorID
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.materials.film import FilmID
from backend.new_core.materials.paper_density import PaperDensity
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
)
from backend.new_core.chroma import Chroma, ChromaID
from backend.new_core.edges import Edges, EdgesID
from backend.test.new_core.test_imposition import imposition_test_sheet
__all__ = [
    "test_imposition_rejects_count_when_nothing_fits",
    "test_product_rejects_empty_blocks",
    "test_paper_rejects_a_density_of_zero",
    "test_paper_accepts_fractional_thickness",
    "test_paper_rejects_thickness_with_more_than_two_decimal_places",
    "test_paper_rejects_a_thickness_of_zero",
    "test_cutter_rejects_a_stack_height_of_zero",
    "test_negative_measure_is_rejected",
    "test_every_invalid_field_is_reported",
    "test_negative_id_is_rejected",
]

_ZERO_CELL = (
    "Imposition: сторона ячейки равна 0, "
    "ширина ячейки=0 мм, высота ячейки=10 мм"
)


def _fitting_imposition() -> Imposition:
    """Handles fitting imposition.

    :return: the Imposition result.
    """
    press_sheet = imposition_test_sheet(200, 300)
    return Imposition(
        target=Format(name="t", height=100, width=100),
        press_sheet=press_sheet,
        edges=Edges(id=EdgesID(0), name="", bleeds=0, spacing=0),
    )


def _block(count: int) -> Part:
    """Handles block.

    :param count: the count.

    :return: the Part result.
    """
    return Part(
        imposition=_fitting_imposition(),
        count=count,
        need_spacing=False,
        operations=(),
    )


def _rejects(message: str, call: object) -> None:
    """Handles rejects.

    :param message: the message.
    :param call: the call.
    """
    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        call()


def test_imposition_rejects_count_when_nothing_fits():
    """A 100 by 100 target on a 50 by 50 press sheet

    is rejected at construction.
    """
    message = "Imposition: на печатный лист влезает 0 целевых листов"

    def _build() -> None:
        """Handles build.
        """
        press_sheet = imposition_test_sheet(50, 50)
        Imposition(
            target=Format(name="t", height=100, width=100),
            press_sheet=press_sheet,
            edges=Edges(id=EdgesID(0), name="", bleeds=0, spacing=0),
        )

    _rejects(message, _build)


def test_product_rejects_empty_blocks():
    """A product with no blocks is rejected at construction."""
    _rejects(
        "Product: нет блоков продукта",
        lambda: Product(parts_markup=Percent(0), blocks=(), operations=()),
    )


def test_paper_rejects_a_density_of_zero():
    """A paper density of 0 is rejected."""
    _rejects(
        "PaperDensity: плотность бумаги меньше или равна 0, плотность=0 г/м²",
        lambda: PaperDensity(0),
    )


def test_paper_accepts_fractional_thickness():
    """A paper thickness of 0.15 mm is accepted."""
    Paper(
        density=PaperDensity(60),
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
            density=PaperDensity(60),
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
            density=PaperDensity(60),
            thickness=Decimal(0),
            type=PaperType("press"),
            price_per_kilo=Money(Decimal(1000)),
        ),
    )


def test_cutter_rejects_a_stack_height_of_zero():
    """A stack height of 0 is rejected."""
    _rejects(
        "cutter: высота стопы равна 0, высота=0 мм",
        lambda: Cutter(id=CutterID(1), name="№ 1", max_stack=0),
    )


@pytest.mark.parametrize(
    ("message", "build"),
    [
        pytest.param(
            "Edges: вылеты меньше 0, вылеты=-1 мм",
            lambda: Imposition(
                target=Format(name="t", height=10, width=10),
                press_sheet=imposition_test_sheet(30, 40),
                edges=Edges(id=EdgesID(0), name="", bleeds=-1, spacing=0),
            ),
            id="bleeds",
        ),
        pytest.param(
            "Edges: поля меньше 0, поля=-1 мм",
            lambda: Imposition(
                target=Format(name="t", height=10, width=10),
                press_sheet=imposition_test_sheet(30, 40),
                edges=Edges(id=EdgesID(0), name="", bleeds=0, spacing=-1),
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
            lambda: Cutter(id=CutterID(1), name="№ 1", max_stack=-1),
            id="stack",
        ),
        pytest.param(
            "Chroma: C меньше 0, C=-1%",
            lambda: Chroma(
                id=ChromaID(0),
                name="",
                cyan=Percent(-1),
                magenta=Percent(0),
                yellow=Percent(0),
                black=Percent(0),
            ),
            id="chroma cyan",
        ),
    ],
)
def test_negative_measure_is_rejected(message: str, build: bool):
    """One negative measure is rejected in its constructor with that text.

    :param message: the message.
    :param build: the build.
    """
    _rejects(message, build)


@pytest.mark.parametrize(
    ("message", "build"),
    [
        pytest.param(
            "Paper: толщина бумаги меньше или равна 0, толщина=0 мм",
            lambda: Paper(
                density=PaperDensity(60),
                thickness=Decimal(0),
                type=PaperType("press"),
                price_per_kilo=Money(Decimal(1000)),
            ),
            id="paper",
        ),
        pytest.param(
            (
                "Edges: вылеты меньше 0, вылеты=-1 мм; "
                "поля меньше 0, поля=-1 мм"
            ),
            lambda: Imposition(
                target=Format(name="t", height=10, width=10),
                press_sheet=imposition_test_sheet(30, 40),
                edges=Edges(id=EdgesID(0), name="", bleeds=-1, spacing=-1),
            ),
            id="imposition",
        ),
        pytest.param(
            (
                "Chroma: C меньше 0, C=-1%; M меньше 0, M=-1%; "
                "Y меньше 0, Y=-1%; K меньше 0, K=-1%"
            ),
            lambda: Chroma(
                id=ChromaID(0),
                name="",
                cyan=Percent(-1),
                magenta=Percent(-1),
                yellow=Percent(-1),
                black=Percent(-1),
            ),
            id="chroma",
        ),
    ],
)
def test_every_invalid_field_is_reported(message: str, build: bool):
    """Every invalid field is named in one error.

    :param message: the message.
    :param build: the build.
    """
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
        pytest.param(
            "laminator id",
            lambda: LaminatorID(-1),
            id="laminator id",
        ),
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
        pytest.param(
            "chroma id",
            lambda: ChromaID(-1),
            id="chroma id",
        ),
    ],
)
def test_negative_id_is_rejected(message: str, build: bool):
    """A negative catalog or entity id is rejected at construction.

    :param message: the message.
    :param build: the build.
    """
    with pytest.raises(InvalidInput, match=message):
        build()
