"""Print-run assembly, order reports, and volume markup tiers."""

import re
from decimal import Decimal

import pytest

from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.operations.laminate.lamination import Lamination
from backend.new_core.operations.print.chroma import Chroma
from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.new_core.materials.film import FilmID
from backend.new_core.values.money import Money
from backend.new_core.values.percent import Percent
from backend.new_core import (
    Accountant,
    InvalidInput,
    Print,
    PrintRun,
)
from backend.test.new_core.test_print_run import (
    _RunPricingFixtures,
    _append_block_operation,
    _estimate,
    assert_tax_scaling_report_prices,
    attach_die_cut_operator,
    build_run_with_free_chroma_pricing,
    build_run_without_block_operations,
    build_worked_run,
    tax_scaling_order,
)


__all__ = [
    "test_factories_append_in_call_order",
    "test_constructor_print_stays_out_of_the_run",
    "test_sheet_cost_report_adds_block_markup_to_volume_markup",
    "test_sheet_cost_report_uses_the_15_percent_volume_band",
    "test_order_report_scales_the_product_by_tax_and_the_order_count",
    "test_print_run_has_no_cost_report",
    "test_print_run_rejects_a_required_count_of_zero",
    "test_sheet_cost_report_uses_volume_markup_tiers",
]

def test_factories_append_in_call_order():
    """Operations append print, laminate, cut, then die cut, in call order.

    Print keeps the block chroma and the press sheet. Laminate keeps the
    block lamination and film. The die cut keeps the operator that was passed.
    """
    run, printing, laminate, cut, ctx = build_worked_run()
    operator = DieCutterOperator(
        id=DieCutterOperatorID(2),
        name="№ 2",
        salary_by_operation=Money(Decimal(8)),
    )
    die_cut = DieCut(operator_id=operator.id)
    _append_block_operation(run, die_cut)
    ctx.die_cut_operators[operator.id] = operator

    assert run.block.operations == (printing, laminate, cut, die_cut)
    assert printing.chroma is Chroma.FOUR_ZERO
    assert run.block.imposition.press_sheet.paper.type.value == "press"
    assert laminate.lamination is Lamination.ONE_ZERO
    assert laminate.film_id == FilmID(1)
    assert die_cut.operator_id is operator.id


def test_constructor_print_stays_out_of_the_run():
    """A Print built by its constructor stays out of the run.

    One factory print prices the press sheet at 10, 11, 5, and 7.8.
    Each target field is that amount divided by 6, and the target total
    is the sum of the four target parts.
    """
    run, printing, _, _, ctx = build_worked_run(
        with_laminate=False, with_cut=False)
    Print(
        printer_id=printing.printer_id,
        operator_id=printing.operator_id,
        chroma=printing.chroma,
    )

    assert run.block.operations == (printing,)
    estimate = _estimate(run, ctx)
    sheet = estimate.sheet_report()
    per_item = estimate.list_report()

    assert sheet.material == Money(Decimal(10))
    assert sheet.startup == Money(Decimal(11))
    assert sheet.work == Money(Decimal(5))
    assert sheet.markup == Money(Decimal("7.8"))
    assert sheet.total() == Money(Decimal("33.8"))
    assert per_item.material == Money(Decimal(10) / Decimal(6))
    assert per_item.startup == Money(Decimal(11) / Decimal(6))
    assert per_item.work == Money(Decimal(5) / Decimal(6))
    assert per_item.markup == Money(Decimal("7.8") / Decimal(6))
    assert (
        per_item.total() == per_item.material +
        per_item.startup +
        per_item.work +
        per_item.markup)


def test_sheet_cost_report_adds_block_markup_to_volume_markup():
    """A 10 percent block markup and a 30 percent volume markup both use the
    base 73.

    The markups are 7.3 and 21.9. The second does not scale the first.
    """
    run, _, _, _, ctx = build_worked_run(parts_markup=Percent(10))

    sheet = _estimate(run, ctx, parts_markup=Percent(10)).sheet_report()

    assert sheet.markup == Money(Decimal("29.2"))
    assert sheet.total() == Money(Decimal("102.2"))


def test_sheet_cost_report_uses_the_15_percent_volume_band():
    """Five press sheets add 15 percent of the ink, not 30."""
    run, _, _, _, ctx = build_run_with_free_chroma_pricing(
        chroma=Chroma.FOUR_ZERO,
        required_count=24,
    )

    sheet = _estimate(run, ctx).sheet_report()

    assert run.imposition_count() == 5
    assert sheet.material == Money(Decimal(4))
    assert sheet.markup == Money(Decimal("0.6"))
    assert sheet.total() == Money(Decimal("4.6"))


def test_order_report_scales_the_product_by_tax_and_the_order_count():
    """Work of 100 with 10 percent markup is 110.

    Then times 100/93, then times 4.

    The run has no operations, so its block report is zero. Income equals
    the order price because material and startup stay zero.
    """
    run, _, _, _, ctx = build_run_without_block_operations()
    order = tax_scaling_order(run)

    estimate = _estimate(run, ctx)
    accountant = Accountant()
    priced = accountant.order_cost_report(
        [estimate],
        order.product.operations,
        order,
    )
    report = accountant.order_report(order, [estimate])

    assert priced.work == Money(Decimal(400))
    assert priced.markup == Money(Decimal(40))
    assert priced.total() == Money(Decimal(440))
    assert_tax_scaling_report_prices(report)


def test_print_run_has_no_cost_report():
    """PrintRun has no cost_report."""
    assert not hasattr(PrintRun, "cost_report")


def test_print_run_rejects_a_required_count_of_zero():
    """A required count of 0 is rejected

    because the run prints no press sheets.
    """
    message = "print_run: печатных листов 0, необходимое количество=0"

    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        build_worked_run(required_count=0)


def _die_cut_only_run(
        required_count: int) -> tuple[PrintRun, _RunPricingFixtures]:
    """Handles die cut only run.

    :param required_count: the required count.

    :return: the tuple[PrintRun, _RunPricingFixtures] result.
    """
    run, _, _, _, ctx = build_run_without_block_operations(
        required_count=required_count,
    )
    attach_die_cut_operator(run, ctx)
    return run, ctx


@pytest.mark.parametrize(
    ("required_count", "press_sheets", "expected_markup"),
    [
        (10, 2, Decimal("2.4")),
        (35, 7, Decimal("1.2")),
        (577, 100, Decimal("0.4")),
        (2908, 500, Decimal(0)),
    ],
)
def test_sheet_cost_report_uses_volume_markup_tiers(
    required_count: int,
    press_sheets: int,
    expected_markup: Decimal,
):
    """Volume markup is 30, 15, 5, or 0 percent by press sheet count.

    :param required_count: the required count.
    :param press_sheets: the press sheets.
    :param expected_markup: the expected markup.
    """
    run, ctx = _die_cut_only_run(required_count)

    assert run.imposition_count() == press_sheets

    sheet = _estimate(run, ctx).sheet_report()

    assert sheet.work == Money(Decimal(8))
    assert sheet.markup == Money(expected_markup)
