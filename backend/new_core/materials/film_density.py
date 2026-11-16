"""Film thickness in microns."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput


__all__ = ["FilmDensity"]

@dataclass(frozen=True, slots=True)
class FilmDensity:
    """Value Object. Film thickness in microns (мкм).
    """

    value: int

    def __post_init__(self) -> None:
        """Validates fields after construction.

        :raises InvalidInput: when the operation fails.
        """
        if self.value <= 0:
            raise InvalidInput(
                subject="FilmDensity",
                reason=(
                    f"плотность плёнки меньше или равна 0, "
                    f"плотность={self.value} мкм"
                ),
            )
