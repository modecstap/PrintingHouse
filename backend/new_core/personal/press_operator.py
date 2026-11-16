"""The person who runs a press, and the salary for one operation."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.personal.name import stripped_required_name
from backend.new_core.values.money import Money


__all__ = [
    "PressOperatorID",
    "PressOperator",
]

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
    name: str
    salary_by_operation: Money

    def __post_init__(self) -> None:
        stripped = stripped_required_name(self.name, "press operator")
        if stripped != self.name:
            object.__setattr__(self, "name", stripped)
