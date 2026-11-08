"""One sheet: its paper and its size, in millimeters."""

from dataclasses import dataclass
from decimal import Decimal

from backend.core.accountant.money import Money
from backend.new_core.errors import InvalidInput
from backend.new_core.paper import Paper


@dataclass(frozen=True)
class Sheet:
    """A paper grade cut to a height and a width."""

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

    def thickness(self) -> int:
        """Returns the thickness of the sheet.

        :return: the thickness of the sheet in mm.
        """
        return self.paper.thickness

    def price(self) -> Money:
        """Returns the price of one sheet.

        :return: the paper price per kilo times the sheet mass.
        """
        return self.paper.price_per_kilo * self.mass_kg()
