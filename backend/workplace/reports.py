from dataclasses import dataclass
from decimal import Decimal

from backend.workplace.accountant.pricing.cutting.models import CutPricing
from backend.workplace.accountant.pricing.lamination.models import \
    LaminationPricing
from backend.workplace.accountant.pricing.printing.models import PressPricing
from backend.workplace.cost_order import DieCutPricing
from backend.workplace.workplaces.cutting.models import CuttingReport
from backend.workplace.workplaces.die_cutting.models import DieCuttingReport
from backend.workplace.workplaces.lamination.models import LaminationReport
from backend.workplace.workplaces.printing.models import PrintingReport


@dataclass(frozen=True)
class PressCase:
    printing: PrintingReport
    press_pricing: PressPricing

@dataclass(frozen=True)
class CuttingCase:
    cutting: CuttingReport
    cut_pricing: CutPricing

@dataclass(frozen=True)
class LaminationCase:
    lamination: LaminationReport
    lamination_pricing: LaminationPricing

@dataclass(frozen=True)
class DieCuttingCase:
    die_cutting: DieCuttingReport
    die_cut_pricing: DieCutPricing

@dataclass(frozen=True)
class PrintingCase:
    item_count: int
    items_per_sheet: int
    sheet_count: int
    internal_sheet_count: int

    press: PressCase
    cutting: CuttingCase
    lamination: LaminationCase
    die_cutting: DieCuttingCase


@dataclass(frozen=True)
class PrintingCost:
    items_per_sheet: int
    sheet_count: int
    unit_cost_price: Decimal
    unit_cost: Decimal
    edition_cost_price: Decimal
    edition_cost: Decimal
    profit_before_tax: Decimal
    profit_after_tax: Decimal


@dataclass(frozen=True)
class CostReport:
    unit_cost_price: Decimal
    unit_cost: Decimal
    edition_cost: Decimal
    profit_after_tax: Decimal
    printing_cost_reports: tuple[PrintingCost, ...]
