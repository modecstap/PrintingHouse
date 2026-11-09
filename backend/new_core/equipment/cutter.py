"""A cutter and the tallest stack it can cut."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput


@dataclass(frozen=True, slots=True)
class CutterID:
    """Value Object. Stable identifier of a cutter in the equipment catalog."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidInput(
                "cutter id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True)
class Cutter:
    """A cutter and the tallest stack it can cut."""

    id: CutterID
    max_stack: int

    def __post_init__(self) -> None:
        """Rejects a stack height that is not positive.

        :raises InvalidInput: if max_stack is below zero, or if it is zero
        after a negative height is rejected.

        :return: nothing.
        """
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
