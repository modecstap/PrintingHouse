from dataclasses import dataclass

from backend.core.accountant.money import Money


@dataclass(frozen=True)
class CostReport:
    target_material: Money
    target_startup: Money
    target_work: Money
    target_total: Money
    press_sheet_material: Money
    press_sheet_startup: Money
    press_sheet_work: Money
    press_sheet_total: Money
