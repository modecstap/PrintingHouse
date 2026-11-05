from dataclasses import dataclass
from decimal import Decimal

from backend.core.accountant.money import Money
from backend.new_core.errors import InvalidInput


@dataclass(frozen=True)
class Paper:
    density: int
    name: str
    price_per_kilo: Money


@dataclass(frozen=True)
class Sheet:
    paper: Paper
    height: int
    width: int

    def __post_init__(self) -> None:
        """Rejects a negative side. Height is checked before width.

        :raises InvalidInput: if height is below zero, or if width is
        below zero after height is accepted.

        :return: nothing. A side of zero stays.
        """
        if self.height < 0:
            raise InvalidInput(
                "sheet",
                f"высота меньше 0, высота={self.height} мм",
            )
        if self.width < 0:
            raise InvalidInput(
                "sheet",
                f"ширина меньше 0, ширина={self.width} мм",
            )

    def mass_kg(self) -> Decimal:
        """Returns the mass of one sheet in kilograms.

        :return: width times height, divided by 1_000_000, times the paper
        density, divided by 1000. Every factor is a Decimal.
        """
        return (
            Decimal(self.width)
            * Decimal(self.height)
            / Decimal(1_000_000)
            * Decimal(self.paper.density)
            / Decimal(1000)
        )
