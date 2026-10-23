from dataclasses import dataclass

from backend.workplace.accountant.money import Money


@dataclass(frozen=True)
class PressPricing:
    cyan: Money
    magenta: Money
    yellow: Money
    black: Money
    paper: Money
    salary: Money