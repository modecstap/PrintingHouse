from decimal import Decimal

import pytest

from backend.models import (
    Chroma,
    CutterInfo,
    Economy,
    Edition,
    Lamination,
    ListSize,
    Operation,
    Order,
    OrderCostReport,
    PressSheet,
    Printing,
    Production,
    Status,
)
from backend.server.helpers.order_factory import OrderFactoryService
from backend.workplace import report_cost


def test_report_matches_fit_order_for_default_order():
    _assert_matches_fit_order(_build_order())


@pytest.mark.parametrize(
    "chroma",
    [
        Chroma.ZERO_ZERO,
        Chroma.ONE_ZERO,
        Chroma.ONE_ONE,
        Chroma.FOUR_ZERO,
        Chroma.FOUR_ONE,
        Chroma.FOUR_FOUR,
    ],
)
def test_report_matches_fit_order_for_chroma(chroma: Chroma):
    _assert_matches_fit_order(_build_order(chroma=chroma))


def test_report_matches_fit_order_for_lamination_one_zero():
    _assert_matches_fit_order(_build_order(lamination=Lamination.ONE_ZERO))


def test_report_matches_fit_order_for_lamination_one_one():
    _assert_matches_fit_order(_build_order(lamination=Lamination.ONE_ONE))


def test_report_matches_fit_order_for_die_cutting():
    _assert_matches_fit_order(_build_order(die_cutting=True))


def test_report_matches_fit_order_for_lamination_and_die_cutting():
    _assert_matches_fit_order(
        _build_order(lamination=Lamination.ONE_ONE, die_cutting=True)
    )


def test_report_matches_fit_order_for_fitting_sheets():
    result = _assert_matches_fit_order(_build_order(sheet_by_fitting=2, count=12))
    assert result.printing_cost_reports[0].sheet_count == 1


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
def test_report_matches_fit_order_for_volume_threshold(count: int, sheet_count: int):
    result = _assert_matches_fit_order(
        _build_order(count=count, sheet_by_fitting=0, unit_count=1)
    )
    assert result.printing_cost_reports[0].sheet_count == sheet_count


def test_report_matches_fit_order_for_two_printings_and_operations():
    printings = [
        _build_printing(
            count=12,
            chroma=Chroma.FOUR_ZERO,
            lamination=Lamination.ONE_ZERO,
            die_cutting=False,
        ),
        _build_printing(
            count=24,
            chroma=Chroma.ONE_ONE,
            lamination=Lamination.DONT,
            die_cutting=True,
        ),
    ]
    operations = [
        Operation(name="fold", description="fold sheets", cost=Decimal("10")),
        Operation(name="pack", description="pack edition", cost=Decimal("3")),
    ]
    _assert_matches_fit_order(
        _build_order(unit_count=1, operations=operations, printings=printings)
    )


def test_report_matches_fit_order_for_unit_count():
    order = _build_order(unit_count=3, count=12)
    _assert_matches_fit_order(order)
    assert order.printings[0].edition.count == 12


def test_report_matches_fit_order_when_fewer_items_than_places():
    _assert_matches_fit_order(_build_order(count=5))


def _assert_matches_fit_order(order: Order) -> OrderCostReport:
    counts = [printing.edition.count for printing in order.printings]
    cost_reports = [printing.cost_report for printing in order.printings]
    status = order.status
    unit_count = order.unit_count
    assert order.cost_report is None

    copy = order.model_copy(deep=True)
    OrderFactoryService().fit_order(copy, Status.SAVED)
    result = report_cost(order)

    assert result == copy.cost_report
    assert result.printing_cost_reports == [
        printing.cost_report for printing in copy.printings
    ]
    assert [printing.edition.count for printing in order.printings] == counts
    assert [printing.cost_report for printing in order.printings] == cost_reports
    assert order.status == status
    assert order.unit_count == unit_count
    assert order.cost_report is None
    return result


def _build_order(
    count: int = 12,
    chroma: Chroma = Chroma.ONE_ZERO,
    lamination: Lamination = Lamination.DONT,
    die_cutting: bool = False,
    sheet_by_fitting: int = 0,
    unit_count: int = 1,
    operations: list[Operation] | None = None,
    printings: list[Printing] | None = None,
) -> Order:
    if printings is None:
        printings = [
            _build_printing(count, chroma, lamination, die_cutting, sheet_by_fitting)
        ]
    if operations is None:
        operations = []
    return Order(
        printings=printings,
        operations=operations,
        economy=Economy(markup=Decimal("20"), tax_rate=Decimal("0.93")),
        unit_count=unit_count,
    )


def _build_printing(
    count: int = 12,
    chroma: Chroma = Chroma.ONE_ZERO,
    lamination: Lamination = Lamination.DONT,
    die_cutting: bool = False,
    sheet_by_fitting: int = 0,
) -> Printing:
    return Printing(
        edition=Edition(
            count=count,
            list_size=ListSize(width=100, height=100, bleeds=0),
            density=150,
            chroma=chroma,
            lamination=lamination,
            die_cutting=die_cutting,
        ),
        production=Production(
            black_ink_cost=Decimal("1.11"),
            ink_cost=Decimal("4.44"),
            printer_salary=Decimal("2.50"),
            lamination_cost=Decimal("3.30"),
            die_cutting_cost=Decimal("7.70"),
            paper_cost=Decimal("80.50"),
            cutting_cost=Decimal("0.40"),
            sheet_by_fitting=sheet_by_fitting,
            press_sheet=PressSheet(width=320, height=450, spacing=0),
            cutter=CutterInfo(stack_height=50),
        ),
    )
