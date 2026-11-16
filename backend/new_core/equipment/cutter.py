"""A cutter and the tallest stack it can cut."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput


__all__ = [
    "CutterID",
    "Cutter",
]

@dataclass(frozen=True, slots=True)
class CutterID:
    """Value Object. Stable identifier of a cutter in the equipment catalog."""

    value: int

    def __post_init__(self) -> None:
        """Validates fields after construction.

        :raises InvalidInput: when the operation fails.
        """
        if self.value < 0:
            raise InvalidInput(
                "cutter id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True)
class Cutter:
    """A cutter and the tallest stack it can cut."""

    id: CutterID
    name: str
    max_stack: int

    def __post_init__(self) -> None:
        """Rejects a blank name and a stack height that is not positive.

        :raises InvalidInput: if the name is blank after strip, if max_stack
        is below zero, or if it is zero after a negative height is rejected.
        """
        stripped = self.name.strip()
        if not stripped:
            raise InvalidInput(
                subject="cutter",
                reason="название не задано",
            )
        if stripped != self.name:
            object.__setattr__(self, "name", stripped)
        if self.max_stack < 0:
            raise InvalidInput(
                "cutter",
                f"высота стопы меньше 0, высота={self.max_stack} мм",
            )
        if self.max_stack == 0:
            raise InvalidInput(
                "cutter",
                f"высота стопы равна 0, высота={self.max_stack} мм",
            )
