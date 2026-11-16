"""An imposition counts targets on a press sheet and the cuts between them."""

import re
from decimal import Decimal

import pytest

from backend.new_core.values.money import Money
from backend.new_core.materials.sheet import SheetID
from backend.new_core import Format, Imposition, InvalidInput, Paper, Sheet
from backend.new_core.materials.paper_density import PaperDensity
from backend.new_core.materials.paper_type import PaperType


def imposition_test_sheet(
    width: int,
    height: int,
    *,
    sheet_id: SheetID | None = None,
) -> Sheet:
    return Sheet(
        id=sheet_id or SheetID(1),
        paper=Paper(
            density=PaperDensity(60),
            thickness=Decimal(1),
            type=PaperType("sheet"),
            price_per_kilo=Money(Decimal(0)),
        ),
        format=Format(name="sheet", height=height, width=width),
    )


def test_imposition_counts_six_and_cuts_ten_on_the_straight_grid():
    """A 10 by 20 target on a 30 by 40 press sheet fits 6 and needs 10 cuts."""
    press_sheet = imposition_test_sheet(30, 40)
    imposition = Imposition(
        target=Format(name="t", height=20, width=10),
        press_sheet=press_sheet,
        bleeds=0,
        spacing=0,
    )

    assert imposition.count() == 6
    assert imposition.cuts() == 10


def test_imposition_counts_twelve_and_cuts_fourteen_on_the_turned_grid():
    """A 10 by 20 target on a 60 by 40 press sheet fits 12 and needs 14 cuts."""
    press_sheet = imposition_test_sheet(60, 40)
    imposition = Imposition(
        target=Format(name="t", height=20, width=10),
        press_sheet=press_sheet,
        bleeds=0,
        spacing=0,
    )

    assert imposition.count() == 12
    assert imposition.cuts() == 14


def test_imposition_counts_six_and_cuts_ten_with_bleeds_and_spacing():
    """A 100 by 100 target, bleeds 5, on a 320 by 450 sheet with spacing 11.

    It fits 6 and needs 10 cuts.
    """
    press_sheet = imposition_test_sheet(320, 450)
    imposition = Imposition(
        target=Format(name="t", height=100, width=100),
        press_sheet=press_sheet,
        bleeds=5,
        spacing=11,
    )

    assert imposition.count() == 6
    assert imposition.cuts() == 10
