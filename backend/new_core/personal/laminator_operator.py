"""The person who runs a laminator, and the salary for one operation."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.values.money import Money


@dataclass(frozen=True, slots=True)
class LaminatorOperatorID:
    """Value Object. Stable identifier of a laminator operator."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidInput(
                "laminator operator id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True)
class LaminatorOperator:
    """The person who runs a laminator, and the salary for one operation."""

    id: LaminatorOperatorID
    salary_by_operation: Money
