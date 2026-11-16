"""Cost reports for worked print runs."""

from decimal import Decimal

import pytest

from backend.new_core.operations.laminate.lamination import Lamination
from backend.new_core.operations.print.chroma import Chroma
from backend.new_core.values.money import Money
from backend.new_core import Accountant, Print
from backend.test.new_core.test_print_run import (
    _append_block_operation,
    attach_die_cut_operator,
    build_run_without_block_operations,
    build_run_with_free_chroma_pricing,
    _estimate,
    build_worked_run,
)


__all__ = [
    "test_cost_report_prices_the_worked_run",
    "test_cost_report_drops_ink_and_printer_salary_for_zero_chroma",
    "test_cost_report_omits_lamination_when_it_is_not_passed",
    "test_cost_report_adds_paper_and_ink_for_a_second_print",
    "test_press_sheet_material_equals_the_chroma_shares",
    "test_list_report_divides_by_the_imposition_count",
    "test_cost_report_is_zero_without_operations",
    "test_cost_report_is_zero_for_lamination_with_no_sides",
    "test_cost_report_prices_two_film_sides_once_for_salary",
    "test_cost_report_adds_the_die_cutter_salary_once",
]

def test_cost_report_prices_the_worked_run():
    """Print, laminate, and cut price the press sheet at 13, 16, 44, and 21.9.

    Two press sheets add 30 percent of 73, so the sheet total is 94.9.
    Each target field is the press amount divided by 6. The block has 3
    sheets, so the block report is the target report times 3.
    """
    run, _, _, _, ctx = build_worked_run()

    assert run.production_count() == 12
    assert run.imposition_count() == 2
    accountant = Accountant()
    sheet = accountant.sheet_cost_report(_estimate(run, ctx))
    per_item = accountant.list_report(_estimate(run, ctx))
    report = accountant.block_cost_report(_estimate(run, ctx))

    assert sheet.material == Money(Decimal(13))
    assert sheet.startup == Money(Decimal(16))
    assert sheet.work == Money(Decimal(44))
    assert sheet.markup == Money(Decimal("21.9"))
    assert sheet.total() == Money(Decimal("94.9"))
    assert per_item.material == Money(Decimal(13) / Decimal(6))
    assert per_item.startup == Money(Decimal(16) / Decimal(6))
    assert per_item.work == Money(Decimal(44) / Decimal(6))
    assert per_item.markup == Money(Decimal("21.9") / Decimal(6))
    assert per_item.total() == Money(Decimal("94.9") / Decimal(6))
    assert (
        per_item.material + per_item.startup + per_item.work + per_item.markup
        == per_item.total()
    )
    assert report.material == per_item.material * 3
    assert report.startup == per_item.startup * 3
    assert report.work == per_item.work * 3
    assert report.markup == per_item.markup * 3
    assert report.total() == (
        report.material + report.startup + report.work + report.markup
    )


def test_cost_report_drops_ink_and_printer_salary_for_zero_chroma():
    """ZERO_ZERO keeps paper and printer startup.

    It drops ink and press salary.

    The press sheet is 9, 16, 39, and 19.2. The total is 83.2.
    """
    run, _, _, _, ctx = build_worked_run(chroma=Chroma.ZERO_ZERO)

    sheet = Accountant.sheet_cost_report(_estimate(run, ctx))

    assert sheet.material == Money(Decimal(9))
    assert sheet.startup == Money(Decimal(16))
    assert sheet.work == Money(Decimal(39))
    assert sheet.markup == Money(Decimal("19.2"))
    assert sheet.total() == Money(Decimal("83.2"))


def test_cost_report_omits_lamination_when_it_is_not_passed():
    """Print and cut, without calling the laminate factory.

    They price the press sheet.

    The press sheet is 10, 11, 40, and 18.3.
    """
    run, _, _, _, ctx = build_worked_run(with_laminate=False)

    sheet = Accountant.sheet_cost_report(_estimate(run, ctx))

    assert sheet.material == Money(Decimal(10))
    assert sheet.startup == Money(Decimal(11))
    assert sheet.work == Money(Decimal(40))
    assert sheet.markup == Money(Decimal("18.3"))
    assert sheet.total() == Money(Decimal("79.3"))


def test_cost_report_adds_paper_and_ink_for_a_second_print():
    """Two FOUR_ZERO prints price the press sheet at 20, 22, 10, and 15.6."""
    run, printing, _, _, ctx = build_worked_run(
        with_laminate=False, with_cut=False)
    second = Print(
        printer_id=printing.printer_id,
        operator_id=printing.operator_id,
        chroma=printing.chroma,
    )
    _append_block_operation(run, second)

    assert run.block.operations == (printing, second)
    assert printing is not second
    sheet = Accountant.sheet_cost_report(_estimate(run, ctx))

    assert sheet.material == Money(Decimal(20))
    assert sheet.startup == Money(Decimal(22))
    assert sheet.work == Money(Decimal(10))
    assert sheet.markup == Money(Decimal("15.6"))
    assert sheet.total() == Money(Decimal("67.6"))


@pytest.mark.parametrize(
    ("chroma", "material"),
    [
        (Chroma.ZERO_ZERO, 0),
        (Chroma.ONE_ZERO, 1),
        (Chroma.ONE_ONE, 2),
        (Chroma.FOUR_ZERO, 4),
        (Chroma.FOUR_ONE, 5),
        (Chroma.FOUR_FOUR, 8),
    ],
)
def test_press_sheet_material_equals_the_chroma_shares(
    chroma: Chroma,
    material: int,
):
    """One print with free paper, startup, and salary.

    :param chroma: the chroma.
    :param material: the material.
    """
    run, _, _, _, ctx = build_run_with_free_chroma_pricing(chroma=chroma)

    sheet = Accountant.sheet_cost_report(_estimate(run, ctx))

    assert sheet.material == Money(Decimal(material))


def test_list_report_divides_by_the_imposition_count():
    """One press sheet is divided by the 6 targets on it.

    Then times 3 block sheets.

    The press sheet is 10, 10, 5, and 7.5. The sheet total is 32.5.
    """
    run, _, _, _, ctx = build_worked_run(
        required_count=3,
        printer_startup=10,
        with_laminate=False,
        with_cut=False,
    )

    accountant = Accountant()
    sheet = accountant.sheet_cost_report(_estimate(run, ctx))
    per_item = accountant.list_report(_estimate(run, ctx))
    report = accountant.block_cost_report(_estimate(run, ctx))

    assert run.imposition_count() == 1
    assert run.block.imposition.count() == 6
    assert sheet.material == Money(Decimal(10))
    assert sheet.startup == Money(Decimal(10))
    assert sheet.work == Money(Decimal(5))
    assert sheet.markup == Money(Decimal("7.5"))
    assert sheet.total() == Money(Decimal("32.5"))
    assert per_item.material == Money(Decimal(10) / Decimal(6))
    assert per_item.startup == Money(Decimal(10) / Decimal(6))
    assert per_item.work == Money(Decimal(5) / Decimal(6))
    assert per_item.markup == Money(Decimal("7.5") / Decimal(6))
    assert per_item.total() == Money(Decimal("32.5") / Decimal(6))
    assert report.material == per_item.material * 3
    assert report.startup == per_item.startup * 3
    assert report.work == per_item.work * 3
    assert report.markup == per_item.markup * 3
    assert report.total() == per_item.total() * 3


def test_cost_report_is_zero_without_operations():
    """No operations price every money field at zero

    and still produce 12 sheets.
    """
    run, _, _, _, ctx = build_run_without_block_operations()

    assert not run.block.operations
    assert run.production_count() == 12
    report = Accountant().block_cost_report(_estimate(run, ctx))

    assert report.material == Money.zero()
    assert report.startup == Money.zero()
    assert report.work == Money.zero()
    assert report.markup == Money.zero()
    assert report.total() == Money.zero()


def test_cost_report_is_zero_for_lamination_with_no_sides():
    """Lamination DONT leaves the press sheet at 10, 11, 40, and 18.3."""
    run, _, _, _, ctx = build_worked_run(lamination=Lamination.DONT)

    sheet = Accountant.sheet_cost_report(_estimate(run, ctx))

    assert sheet.material == Money(Decimal(10))
    assert sheet.startup == Money(Decimal(11))
    assert sheet.work == Money(Decimal(40))
    assert sheet.markup == Money(Decimal("18.3"))
    assert sheet.total() == Money(Decimal("79.3"))


def test_cost_report_prices_two_film_sides_once_for_salary():
    """Two film sides price material at 6, startup at 5,

    and salary once at 4.
    """
    run, _, _, _, ctx = build_worked_run(
        lamination=Lamination.ONE_ONE,
        with_print=False,
        with_cut=False,
    )

    sheet = Accountant.sheet_cost_report(_estimate(run, ctx))

    assert sheet.material == Money(Decimal(6))
    assert sheet.startup == Money(Decimal(5))
    assert sheet.work == Money(Decimal(4))
    assert sheet.markup == Money(Decimal("4.5"))
    assert sheet.total() == Money(Decimal("19.5"))


def test_cost_report_adds_the_die_cutter_salary_once():
    """A die cut adds only the salary 8.

    The target work is 8 divided by 6.
    """
    run, _, _, _, ctx = build_run_without_block_operations()
    attach_die_cut_operator(run, ctx)

    accountant = Accountant()
    sheet = accountant.sheet_cost_report(_estimate(run, ctx))
    per_item = accountant.list_report(_estimate(run, ctx))

    assert sheet.material == Money(Decimal(0))
    assert sheet.startup == Money(Decimal(0))
    assert sheet.work == Money(Decimal(8))
    assert sheet.markup == Money(Decimal("2.4"))
    assert sheet.total() == Money(Decimal("10.4"))
    assert per_item.work == Money(Decimal(8) / Decimal(6))
