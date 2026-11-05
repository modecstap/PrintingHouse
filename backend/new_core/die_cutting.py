from dataclasses import dataclass

from backend.core.accountant.money import Money


@dataclass(frozen=True)
class DieCutterOperator:
    id: int
    salary_by_operation: Money
