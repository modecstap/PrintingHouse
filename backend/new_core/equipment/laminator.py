"""A laminator and its startup price."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.values.money import Money


@dataclass(frozen=True, slots=True)
class LaminatorID:
    """Value Object. Stable identifier of a laminator in the equipment catalog."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidInput(
                "laminator id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True)
class Laminator:
    """A laminator and its startup price."""

    id: LaminatorID
    name: str
    startup: Money

    def __post_init__(self) -> None:
        stripped = self.name.strip()
        if not stripped:
            raise InvalidInput(
                subject="laminator",
                reason="название не задано",
            )
        if stripped != self.name:
            object.__setattr__(self, "name", stripped)
