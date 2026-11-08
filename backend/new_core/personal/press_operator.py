"""The person who runs a press, and the salary for one operation."""

from dataclasses import dataclass

from backend.new_core.values.money import Money


@dataclass(frozen=True)
class PressOperator:
    """The person who runs a press, and the salary for one operation."""

    id: int
    salary_by_operation: Money
