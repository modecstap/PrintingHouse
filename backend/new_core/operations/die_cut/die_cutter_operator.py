"""The person who runs a die cutter, and the salary for one operation."""

from dataclasses import dataclass

from backend.new_core.accountant.money import Money


@dataclass(frozen=True)
class DieCutterOperator:
    """The person who runs a die cutter, and the salary for one operation."""

    id: int
    salary_by_operation: Money
