from decimal import Decimal

import pytest

from backend.core.accountant.money import Money
from backend.core.accountant.pricing.cutting import CuttingCalculation
from backend.core.accountant.pricing.die_cutting import (
    DieCuttingCalculation,
)
from backend.core.accountant.pricing.lamination import (
    LaminationCalculation,
)
from backend.core.accountant.pricing.printing import PrintingCalculation
from backend.core.administrator import Administrator
from backend.core.order import (
    List,
    Order,
    OrderSpecification,
    Printing,
    PrintingSpecification,
)
from backend.core.sheet.format import SheetFormat
from backend.core.sheet.sheet import Sheet
from backend.core.workplaces.lamination.models import Lamination
from backend.core.workplaces.printing.models import Chroma


def _loaded(
    density: int,
    width: int,
    height: int,
    spacing: int,
    item: List,
    count: int,
    cost: str = "0",
) -> tuple[Order, dict[int, Sheet]]:
    zero = Money(Decimal(0))
    rate = Money(Decimal(cost))
    sheet = Sheet(SheetFormat("", height, width), density, rate)
    printing = Printing(
        specification=PrintingSpecification(
            count=count,
            chroma=Chroma.ZERO_ZERO,
            lamination=Lamination.DONT,
            die_cutting=False,
            spacing=spacing,
            press_sheet=1,
            list=item,
            sheet_by_fitting=0,
        ),
        stack_height=50,
        press_pricing=PrintingCalculation(zero, zero, zero, zero, zero),
        cut_pricing=CuttingCalculation(zero),
        lamination_pricing=LaminationCalculation(zero, zero, zero),
        die_cut_pricing=DieCuttingCalculation(zero),
    )
    order = Order(
        specification=OrderSpecification(
            unit_count=1,
            markup=Decimal("0"),
            operations=(),
        ),
        tax_rate=Decimal("1"),
        printings=(printing,),
    )
    return order, {1: sheet}


def test_report_cost_counts_twelve_items_on_a_plain_sheet():
    order, sheets = _loaded(150, 320, 450, 0, List(100, 100, 0), 1, "10")
    result = Administrator().report_cost(order, sheets)
    report = result.printing_cost_reports[0]

    assert report.items_per_sheet == 12
    assert report.edition_cost_price == Decimal("0.22")


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
    order, sheets = _loaded(150, 320, 450, 0, List(100, 100, 0), count)
    result = Administrator().report_cost(order, sheets)

    assert result.printing_cost_reports[0].sheet_count == sheet_count


def test_report_cost_counts_six_items_and_two_sheets_with_field_and_bleeds():
    order, sheets = _loaded(150, 320, 450, 11, List(100, 100, 5), 12)
    result = Administrator().report_cost(order, sheets)
    report = result.printing_cost_reports[0]

    assert (report.items_per_sheet, report.sheet_count) == (6, 2)


def test_report_cost_rejects_a_sheet_that_fits_no_items():
    order, sheets = _loaded(150, 50, 50, 0, List(100, 100, 0), 1)

    with pytest.raises(ZeroDivisionError):
        Administrator().report_cost(order, sheets)
