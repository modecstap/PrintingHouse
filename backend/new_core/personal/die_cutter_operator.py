"""The person who runs a die cutter, and the salary for one operation."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.values.money import Money


@dataclass(frozen=True, slots=True)
class DieCutterOperatorID:
    """Value Object. Stable identifier of a die cutter operator."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidInput(
                "die cutter operator id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True)
class DieCutterOperator:
    """The person who runs a die cutter, and the salary for one operation."""

    id: DieCutterOperatorID
    salary_by_operation: Money
