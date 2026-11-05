from dataclasses import dataclass

from backend.core.accountant.money import Money


@dataclass(frozen=True)
class Printer:
    id: int
    startup: Money
    cyan: Money
    magenta: Money
    yellow: Money
    black: Money


@dataclass(frozen=True)
class PressOperator:
    id: int
    salary_by_operation: Money
