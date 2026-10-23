from dataclasses import dataclass
from decimal import Decimal

from backend.workplace.accountant.pricing.calculatable import Calculatable


@dataclass(frozen=True)
class PrintingCase:
    item_count: int
    items_per_sheet: int
    sheet_count: int
    internal_sheet_count: int
    calculations: tuple[Calculatable, ...]


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
