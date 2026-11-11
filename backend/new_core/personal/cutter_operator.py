"""The person who runs a cutter, and the salary for one operation."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.values.money import Money


@dataclass(frozen=True, slots=True)
class CutterOperatorID:
    """Value Object. Stable identifier of a cutter operator."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidInput(
                "cutter operator id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True)
class CutterOperator:
    """The person who runs a cutter, and the salary for one operation."""

    id: CutterOperatorID
    name: str
    salary_by_operation: Money

    def __post_init__(self) -> None:
        stripped = self.name.strip()
        if not stripped:
            raise InvalidInput(
                subject="cutter operator",
                reason="название не задано",
            )
        if stripped != self.name:
            object.__setattr__(self, "name", stripped)
