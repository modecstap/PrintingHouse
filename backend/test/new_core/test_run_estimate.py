"""RunEstimate.create validation."""

from dataclasses import replace

import pytest

from backend.new_core.accountant.pricing.print_pricing import PrintPricing
from backend.new_core.accountant.run_estimate import RunEstimate
from backend.new_core.order.order import OrderID
from backend.new_core.print_run.print_run import PrintRun, PrintRunID
from backend.test.new_core.test_print_run import build_worked_run


def test_create_rejects_strategies_for_different_runs():
    run_a, printing, _, _, ctx = build_worked_run()
    run_b = PrintRun(
        id=PrintRunID(99),
        for_order=OrderID(2),
        block=run_a.block,
        required_count=run_a.required_count,
    )
    strategy_a = PrintPricing(
        printer=ctx.printers[printing.printer_id],
        operator=ctx.press_operators[printing.operator_id],
        chroma=printing.chroma,
        print_run=run_a,
    )
    strategy_b = PrintPricing(
        printer=ctx.printers[printing.printer_id],
        operator=ctx.press_operators[printing.operator_id],
        chroma=printing.chroma,
        print_run=run_b,
    )

    with pytest.raises(ValueError, match="same run"):
        RunEstimate.create((strategy_a, strategy_b))


def test_create_requires_strategies_or_explicit_run():
    with pytest.raises(ValueError, match="strategies or an explicit run"):
        RunEstimate.create(())


def test_create_accepts_empty_strategies_with_explicit_run():
    run, *_ = build_worked_run(with_print=False, with_laminate=False, with_cut=False)

    estimate = RunEstimate.create((), run=run)

    assert estimate.imposition_count() == run.imposition_count()
