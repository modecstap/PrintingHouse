"""A film name, its price, and its density."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.values.money import Money


@dataclass(frozen=True, slots=True)
class FilmID:
    """Value Object. Stable identifier of a film in the materials catalog."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidInput(
                "film id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True, slots=True)
class Film:
    """
    Entity. A film row in the materials catalog.

    Density does not change the money of a run.
    The constructor does not check the sign of density.
    """

    id: FilmID
    name: str
    price: Money
    density: int
