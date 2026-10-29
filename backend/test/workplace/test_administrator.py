from decimal import Decimal

import pytest

from backend.workplace.accountant.money import Money
from backend.workplace.accountant.pricing.cutting import CuttingCalculation
from backend.workplace.accountant.pricing.die_cutting import (
    DieCuttingCalculation,
)
from backend.workplace.accountant.pricing.lamination import (
    LaminationCalculation,
)
from backend.workplace.accountant.pricing.printing import PrintingCalculation
from backend.workplace.administrator import Administrator
from backend.workplace.cost_order import List, Order, Printing
from backend.workplace.workplaces.lamination.models import Lamination
from backend.workplace.workplaces.printing.models import Chroma, PressSheet


def _order(
    press_sheet: PressSheet,
    item: List,
    count: int,
) -> Order:
    zero = Money(Decimal(0))
    printing = Printing(
        count=count,
        chroma=Chroma.ZERO_ZERO,
        lamination=Lamination.DONT,
        die_cutting=False,
        sheet_by_fitting=0,
        stack_height=50,
        press_sheet=press_sheet,
        list=item,
        press_pricing=PrintingCalculation(zero, zero, zero, zero, zero, zero),
        cut_pricing=CuttingCalculation(zero),
        lamination_pricing=LaminationCalculation(zero, zero, zero),
        die_cut_pricing=DieCuttingCalculation(zero),
    )
    return Order(
        unit_count=1,
        tax_rate=Decimal("1"),
        markup=Decimal("0"),
        operations=(),
        printings=(printing,),
    )


def test_report_cost_counts_twelve_items_on_a_plain_sheet():
    order = _order(PressSheet(150, 320, 450, 0), List(100, 100, 0), 1)
    result = Administrator().report_cost(order)

    assert result.printing_cost_reports[0].items_per_sheet == 12


@pytest.mark.parametrize(
    ("count", "sheet_count"),
    [
        (48, 4),
        (60, 5),
        (1188, 99),
        (1200, 100),
        (5988, 499),
        (6000, 500),
    ],
)
def test_report_cost_counts_sheets_from_twelve_items(
    count: int,
    sheet_count: int,
):
    order = _order(PressSheet(150, 320, 450, 0), List(100, 100, 0), count)
    result = Administrator().report_cost(order)

    assert result.printing_cost_reports[0].sheet_count == sheet_count


def test_report_cost_counts_six_items_and_two_sheets_with_field_and_bleeds():
    order = _order(PressSheet(150, 320, 450, 11), List(100, 100, 5), 12)
    result = Administrator().report_cost(order)
    report = result.printing_cost_reports[0]

    assert (report.items_per_sheet, report.sheet_count) == (6, 2)


def test_report_cost_rejects_a_sheet_that_fits_no_items():
    order = _order(PressSheet(150, 50, 50, 0), List(100, 100, 0), 1)

    with pytest.raises(ZeroDivisionError):
        Administrator().report_cost(order)
