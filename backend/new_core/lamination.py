from dataclasses import dataclass

from backend.core.accountant.money import Money


@dataclass(frozen=True)
class Film:
    """A film name and its price.

    Density does not change the money of a run.
    The constructor does not check the sign of density.
    """

    name: str
    price: Money
    density: int


@dataclass(frozen=True)
class Laminator:
    id: int
    startup: Money


@dataclass(frozen=True)
class LaminatorOperator:
    id: int
    salary_by_operation: Money
