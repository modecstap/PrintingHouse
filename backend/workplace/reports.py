from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PrintingReport:
    mass_kg: Decimal
    used_ink: tuple[int, int, int, int]
    sheet_count: int
    human_operations: int


@dataclass(frozen=True)
class CuttingReport:
    human_cuts: int


@dataclass(frozen=True)
class LaminationReport:
    film_sides: int


@dataclass(frozen=True)
class DieCuttingReport:
    sheet_count: int


@dataclass(frozen=True)
class PrintingCase:
    item_count: int
    items_per_sheet: int
    sheet_count: int
    internal_sheet_count: int
    printing: PrintingReport
    cutting: CuttingReport
    lamination: LaminationReport
    die_cutting: DieCuttingReport
    paper_cost: Decimal
    ink_cost: Decimal
    black_ink_cost: Decimal
    printer_salary: Decimal
    cutting_cost: Decimal
    lamination_cost: Decimal
    die_cutting_cost: Decimal


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
