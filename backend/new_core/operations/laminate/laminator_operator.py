"""The person who runs a laminator, and the salary for one operation."""

from dataclasses import dataclass

from backend.core.accountant.money import Money


@dataclass(frozen=True)
class LaminatorOperator:
    """The person who runs a laminator, and the salary for one operation."""

    id: int
    salary_by_operation: Money
