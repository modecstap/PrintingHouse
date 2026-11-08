"""A film name, its price, and its density."""

from dataclasses import dataclass

from backend.new_core.accountant.money import Money


@dataclass(frozen=True, slots=True)
class Film:
    """
    Value Object. A film name, its price, and its density.

    Density does not change the money of a run.
    The constructor does not check the sign of density.
    """

    name: str
    price: Money
    density: int
