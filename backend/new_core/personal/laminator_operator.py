"""The person who runs a laminator, and the salary for one operation."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.personal.name import stripped_required_name
from backend.new_core.values.money import Money


__all__ = [
    "LaminatorOperatorID",
    "LaminatorOperator",
]

@dataclass(frozen=True, slots=True)
class LaminatorOperatorID:
    """Value Object. Stable identifier of a laminator operator."""

    value: int

    def __post_init__(self) -> None:
        """Validates fields after construction.

        :raises InvalidInput: when the operation fails.
        """
        if self.value < 0:
            raise InvalidInput(
                "laminator operator id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True)
class LaminatorOperator:
    """The person who runs a laminator, and the salary for one operation."""

    id: LaminatorOperatorID
    name: str
    salary_by_operation: Money

    def __post_init__(self) -> None:
        """Validates fields after construction.
        """
        stripped = stripped_required_name(self.name, "laminator operator")
        if stripped != self.name:
            object.__setattr__(self, "name", stripped)
