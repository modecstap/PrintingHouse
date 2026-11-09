"""Build run estimates from operations and resolved equipment."""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.new_core.accountant.pricing.cut_pricing import CutPricing
from backend.new_core.accountant.pricing.die_cut_pricing import DieCutPricing
from backend.new_core.accountant.pricing.laminate_pricing import LaminatePricing
from backend.new_core.accountant.pricing.print_pricing import PrintPricing
from backend.new_core.accountant.pricing_strategy import PricingStrategy
from backend.new_core.accountant.run_estimate import RunEstimate
from backend.new_core.equipment.cutter import Cutter
from backend.new_core.equipment.laminator import Laminator
from backend.new_core.equipment.printer import Printer
from backend.new_core.operations.cut.cut import Cut
from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.new_core.operations.laminate.laminate import Laminate
from backend.new_core.operations.print.print import Print
from backend.new_core.personal.cutter_operator import CutterOperator
from backend.new_core.personal.die_cutter_operator import DieCutterOperator
from backend.new_core.personal.laminator_operator import LaminatorOperator
from backend.new_core.personal.press_operator import PressOperator
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.equipment.cutter import CutterID
from backend.new_core.equipment.laminator import LaminatorID
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.personal.cutter_operator import CutterOperatorID
from backend.new_core.personal.die_cutter_operator import DieCutterOperatorID
from backend.new_core.personal.laminator_operator import LaminatorOperatorID
from backend.new_core.personal.press_operator import PressOperatorID


@dataclass
class RunPricingContext:
    """Equipment and staff looked up by id when pricing run operations."""

    printers: dict[PrinterID, Printer] = field(default_factory=dict)
    press_operators: dict[PressOperatorID, PressOperator] = field(default_factory=dict)
    laminators: dict[LaminatorID, Laminator] = field(default_factory=dict)
    laminator_operators: dict[LaminatorOperatorID, LaminatorOperator] = field(
        default_factory=dict,
    )
    cutter_operators: dict[CutterOperatorID, CutterOperator] = field(
        default_factory=dict,
    )
    die_cut_operators: dict[DieCutterOperatorID, DieCutterOperator] = field(
        default_factory=dict,
    )
    cutters: dict[CutterID, Cutter] = field(default_factory=dict)


def operation_reports(
        run: PrintRun,
        ctx: RunPricingContext,
) -> RunEstimate:
    """Turns run operations into pricing strategies for one estimate."""
    strategies: list[PricingStrategy] = []
    for operation in run.operations:
        if isinstance(operation, Print):
            strategies.append(
                PrintPricing(
                    printer=ctx.printers[operation.printer_id],
                    operator=ctx.press_operators[operation.operator_id],
                    chroma=operation.chroma,
                    paper=operation.paper,
                    print_run=run,
                ),
            )
        elif isinstance(operation, Laminate):
            strategies.append(
                LaminatePricing(
                    laminator=ctx.laminators[operation.laminator_id],
                    operator=ctx.laminator_operators[operation.operator_id],
                    lamination=operation.lamination,
                    film=operation.film,
                    print_run=run,
                ),
            )
        elif isinstance(operation, Cut):
            strategies.append(
                CutPricing(
                    cutter=operation.cutter,
                    operator=ctx.cutter_operators[operation.operator_id],
                    print_run=run,
                ),
            )
        elif isinstance(operation, DieCut):
            strategies.append(
                DieCutPricing(
                    operator=ctx.die_cut_operators[operation.operator_id],
                    print_run=run,
                ),
            )
        else:
            raise TypeError(
                f"Unsupported run operation type: {type(operation).__name__}",
            )
    return RunEstimate.create(strategies, run=run)
