from dataclasses import dataclass
from decimal import Decimal

from backend.workplace.accountant.pricing.cutting import CuttingCalculation
from backend.workplace.accountant.pricing.die_cutting import \
    DieCuttingCalculation
from backend.workplace.accountant.pricing.lamination import \
    LaminationCalculation
from backend.workplace.accountant.pricing.printing import \
    PrintingCalculation
from backend.workplace.workplaces.lamination.models import Lamination
from backend.workplace.workplaces.printing.models import PressSheet, Chroma


@dataclass(frozen=True)
class List:
    width: int
    height: int
    bleeds: int

@dataclass(frozen=True)
class Printing:
    count: int
    chroma: Chroma
    lamination: Lamination
    die_cutting: bool
    sheet_by_fitting: int
    stack_height: int
    press_sheet: PressSheet
    list: List
    press_pricing: PrintingCalculation
    cut_pricing: CuttingCalculation
    lamination_pricing: LaminationCalculation
    die_cut_pricing: DieCuttingCalculation


@dataclass(frozen=True)
class Order:
    unit_count: int
    tax_rate: Decimal
    markup: Decimal
    operation_costs: tuple[Decimal, ...]
    printings: tuple[Printing, ...]
