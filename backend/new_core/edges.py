"""Bleeds and press-sheet spacing for imposition."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput


__all__ = [
    "EdgesID",
    "Edges",
]


@dataclass(frozen=True, slots=True)
class EdgesID:
    """Value Object. Stable identifier of an edges row in the catalog."""

    value: int

    def __post_init__(self) -> None:
        """Rejects negative ids.

        :raises InvalidInput: when ``value`` is below zero.
        """
        if self.value < 0:
            raise InvalidInput(
                "edges id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True, slots=True)
class Edges:
    """Entity. One edges catalog row: name, bleeds and spacing in mm."""

    id: EdgesID
    name: str
    bleeds: int
    spacing: int

    def __post_init__(self) -> None:
        """Rejects negative bleeds or spacing.

        :raises InvalidInput: if bleeds or spacing is below zero. Both
        failures are reported together.
        """
        reasons: list[str] = []
        if self.bleeds < 0:
            reasons.append(
                f"вылеты меньше 0, вылеты={self.bleeds} мм",
            )
        if self.spacing < 0:
            reasons.append(
                f"поля меньше 0, поля={self.spacing} мм",
            )
        if reasons:
            raise InvalidInput(
                subject="Edges",
                reason=reasons,
            )