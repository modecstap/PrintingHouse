import re
from decimal import Decimal

import pytest

from backend.core.accountant.money import Money
from backend.new_core import Imposition, InvalidInput, Paper, Sheet


def _sheet(width: int, height: int) -> Sheet:
    return Sheet(
        paper=Paper(density=0, name="sheet", price_per_kilo=Money(Decimal(0))),
        height=height,
        width=width,
    )


def test_imposition_counts_six_and_cuts_ten_on_the_straight_grid():
    """A 10 by 20 target on a 30 by 40 press sheet fits 6 and needs 10 cuts."""
    imposition = Imposition(
        target=_sheet(10, 20),
        press_sheet=_sheet(30, 40),
        bleeds=0,
        spacing=0,
    )

    assert imposition.count() == 6
    assert imposition.cuts() == 10


def test_imposition_counts_twelve_and_cuts_fourteen_on_the_turned_grid():
    """A 10 by 20 target on a 60 by 40 press sheet fits 12 and needs 14 cuts."""
    imposition = Imposition(
        target=_sheet(10, 20),
        press_sheet=_sheet(60, 40),
        bleeds=0,
        spacing=0,
    )

    assert imposition.count() == 12
    assert imposition.cuts() == 14


def test_imposition_counts_six_and_cuts_ten_with_bleeds_and_spacing():
    """A 100 by 100 target with bleeds 5 on a 320 by 450 sheet with spacing 11 fits 6 and needs 10 cuts."""
    imposition = Imposition(
        target=_sheet(100, 100),
        press_sheet=_sheet(320, 450),
        bleeds=5,
        spacing=11,
    )

    assert imposition.count() == 6
    assert imposition.cuts() == 10


def test_imposition_rejects_a_zero_cell_side():
    """A target width of 0 makes count and cuts reject the zero cell side."""
    imposition = Imposition(
        target=_sheet(0, 10),
        press_sheet=_sheet(30, 40),
        bleeds=0,
        spacing=0,
    )
    message = (
        "imposition: сторона ячейки равна 0, "
        "ширина ячейки=0 мм, высота ячейки=10 мм"
    )

    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        imposition.count()
    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        imposition.cuts()
