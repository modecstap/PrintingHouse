import inspect
from decimal import Decimal

import pytest

from backend.core.accountant.money import Money
from backend.core.order import List
from backend.core.sheet.format import SheetFormat, standard_formats
from backend.core.sheet.sheet import Sheet


def test_standard_formats_returns_six_sizes_and_takes_no_repository():
    formats = standard_formats()

    assert [(item.name, item.height, item.width) for item in formats] == [
        ("\u04101", 594, 841),
        ("\u04102", 420, 594),
        ("\u04103", 297, 420),
        ("\u04104", 210, 297),
        ("\u04105", 148, 210),
        ("\u04106", 105, 148),
    ]
    assert list(inspect.signature(standard_formats).parameters) == []


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
def test_sheet_counts_items_and_cuts(
    sheet_width: int,
    sheet_height: int,
    spacing: int,
    item_width: int,
    item_height: int,
    bleeds: int,
    items: int,
    cuts: int,
):
    sheet = Sheet(
        SheetFormat("sheet", sheet_height, sheet_width),
        150,
        Money(Decimal("0")),
    )
    item = List(item_width, item_height, bleeds)

    assert sheet.item_count(item, spacing) == items
    assert sheet.cut_needed(item, spacing) == cuts


def test_sheet_rejects_a_zero_item_side():
    sheet = Sheet(SheetFormat("sheet", 450, 320), 150, Money(Decimal("0")))
    item = List(0, 100, 0)

    with pytest.raises(ZeroDivisionError):
        sheet.item_count(item, 0)
    with pytest.raises(ZeroDivisionError):
        sheet.cut_needed(item, 0)


def test_reprice_changes_density_and_cost_and_keeps_the_format():
    sheet = Sheet(SheetFormat("450 x 320", 450, 320), 150, Money(Decimal("10")))

    sheet.reprice(200, Money(Decimal("12.5")))

    assert sheet.density == 200
    assert sheet.cost == Money(Decimal("12.5"))
    assert (sheet.format.name, sheet.format.height, sheet.format.width) == (
        "450 x 320",
        450,
        320,
    )
    assert sheet.id is None
    assert sheet.version == 0
