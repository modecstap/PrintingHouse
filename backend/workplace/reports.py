from dataclasses import dataclass
from decimal import Decimal

from backend.workplace.accountant.pricing.cutting import CuttingCalculation
from backend.workplace.accountant.pricing.die_cutting import \
    DieCuttingCalculation
from backend.workplace.accountant.pricing.lamination import \
    LaminationCalculation
from backend.workplace.accountant.pricing.printing import \
    PrintingCalculation


@dataclass(frozen=True)
class PrintingCase:
    item_count: int
    items_per_sheet: int
    sheet_count: int
    internal_sheet_count: int

    press: PrintingCalculation
    cutting: CuttingCalculation
    lamination: LaminationCalculation
    die_cutting: DieCuttingCalculation


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
