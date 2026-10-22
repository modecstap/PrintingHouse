from dataclasses import dataclass
from decimal import Decimal

from backend.models.production import Production


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
    production: Production
