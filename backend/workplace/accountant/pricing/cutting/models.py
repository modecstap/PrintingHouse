from dataclasses import dataclass

from backend.aggregate.printer.money import Money


@dataclass(frozen=True)
class CutPricing:
    salary: Money
