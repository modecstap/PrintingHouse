import pytest

from backend.workplace.cost_order import List
from backend.workplace.placement import place_on_sheet
from backend.workplace.workplaces.printing.models import PressSheet


@pytest.mark.parametrize(
    (
        "sheet_width",
        "sheet_height",
        "spacing",
        "item_width",
        "item_height",
        "bleeds",
        "items",
        "cuts",
    ),
    [
        (320, 450, 0, 100, 100, 0, 12, 14),
        (320, 450, 11, 100, 100, 5, 6, 10),
        (200, 300, 0, 100, 50, 0, 12, 14),
        (300, 200, 0, 140, 90, 0, 4, 8),
    ],
)
def test_place_on_sheet_counts_items_and_cuts(
    sheet_width: int,
    sheet_height: int,
    spacing: int,
    item_width: int,
    item_height: int,
    bleeds: int,
    items: int,
    cuts: int,
):
    result = place_on_sheet(
        PressSheet(150, sheet_width, sheet_height, spacing),
        List(item_width, item_height, bleeds),
    )

    assert (result.items_per_sheet, result.cut_count) == (items, cuts)


def test_place_on_sheet_rejects_a_zero_item_side():
    with pytest.raises(ZeroDivisionError):
        place_on_sheet(PressSheet(150, 320, 450, 0), List(0, 100, 0))
