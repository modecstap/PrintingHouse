"""The person who runs a press, and the salary for one operation."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.values.money import Money


@dataclass(frozen=True, slots=True)
class PressOperatorID:
    """Value Object. Stable identifier of a press operator."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidInput(
                "press operator id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True)
class PressOperator:
    """The person who runs a press, and the salary for one operation."""

    id: PressOperatorID
    salary_by_operation: Money
