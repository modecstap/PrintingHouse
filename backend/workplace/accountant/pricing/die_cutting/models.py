from dataclasses import dataclass

from backend.workplace.accountant.money import Money


@dataclass(frozen=True)
class DieCutPricing:
    salary: Money
