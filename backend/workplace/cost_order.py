from dataclasses import dataclass
from decimal import Decimal

from backend.workplace.chroma import Chroma
from backend.workplace.lamination import Lamination
from backend.workplace.money import Money

@dataclass(frozen=True)
class List:
    width: int
    height: int
    bleeds: int

@dataclass(frozen=True)
class PressSheet:
    density: int
    width: int
    height: int
    spacing: int

@dataclass(frozen=True)
class PressPricing:
    cyan: Money
    magenta: Money
    yellow: Money
    black: Money
    paper: Money
    salary: Money

@dataclass(frozen=True)
class CutPricing:
    salary: Money

@dataclass(frozen=True)
class LaminationPricing:
    startup: Money
    film_cost: Money
    salary: Money

@dataclass(frozen=True)
class DieCutPricing:
    salary: Money

@dataclass(frozen=True)
class CostPrinting:
    count: int
    chroma: Chroma
    lamination: Lamination
    die_cutting: bool
    sheet_by_fitting: int
    stack_height: int
    press_sheet: PressSheet
    list: List
    press_pricing: PressPricing
    cut_pricing: CutPricing
    lamination_pricing: LaminationPricing
    die_cut_pricing: DieCutPricing


@dataclass(frozen=True)
class CostOrder:
    unit_count: int
    tax_rate: Decimal
    markup: Decimal
    operation_costs: tuple[Decimal, ...]
    printings: tuple[CostPrinting, ...]
