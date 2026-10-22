from dataclasses import dataclass
from decimal import Decimal

from backend.workplace.chroma import Chroma
from backend.workplace.lamination import Lamination
from backend.workplace.money import Money


@dataclass(frozen=True)
class CostPrinting:
    count: int
    density: int
    chroma: Chroma
    lamination: Lamination
    die_cutting: bool
    sheet_by_fitting: int
    stack_height: int
    press_sheet_width: int
    press_sheet_height: int
    press_sheet_spacing: int
    list_width: int
    list_height: int
    list_bleeds: int
    paper_cost: Decimal
    ink_cost: Decimal
    black_ink_cost: Decimal
    printer_salary: Decimal
    cutting_cost: Decimal
    lamination_cost: Decimal
    die_cutting_cost: Decimal

@dataclass(frozen=True)
class List:
    width: int
    height: int
    bleeds: int

@dataclass(frozen=True)
class PressSheet:
    width: int
    height: int
    spacing: int

@dataclass(frozen=True)
class PressPricing:
    cyan: Money
    magenta: Money
    yellow: Money
    black: Money
    printer_salary: Money

@dataclass(frozen=True)
class CuttingPricing:
    salary: Money

@dataclass(frozen=True)
class LaminationPricing:
    film_cost: Money
    salary: Money

@dataclass(frozen=True)
class DieCuttingPricing:
    salary: Money

@dataclass(frozen=True)
class CostOrder:
    unit_count: int
    tax_rate: Decimal
    markup: Decimal
    operation_costs: tuple[Decimal, ...]
    printings: tuple[CostPrinting, ...]
