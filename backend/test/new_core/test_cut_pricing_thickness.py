"""Cut stack sizing with fractional paper thickness."""

from decimal import Decimal

from backend.new_core.accountant.pricing.cut_pricing import CutPricing
from backend.test.new_core.test_print_run import build_worked_run


def test_cut_pricing_sheets_in_stack_with_fractional_thickness():
    """Stack sheet count uses Decimal thickness (ceil(50 / 0.15) == 334)."""
    run, _, _, cut, ctx = build_worked_run(
        paper_thickness=Decimal("0.15"),
        max_stack=50,
    )
    pricing = CutPricing(
        cutter=ctx.cutters[cut.cutter_id],
        operator=ctx.cutter_operators[cut.operator_id],
        print_run=run,
    )
    assert pricing._sheets_in_stack() == 334
