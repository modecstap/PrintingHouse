"""One sheet: its paper and its size, in millimeters."""

from dataclasses import dataclass
from decimal import Decimal

from backend.new_core.values.money import Money
from backend.new_core.errors import InvalidInput
from backend.new_core.materials.paper import Paper


@dataclass(frozen=True, slots=True)
class Sheet:
    """
    Value Object. One sheet of a paper grade, with its height and width in millimeters.
    """

    paper: Paper
    height: int
    width: int

    def __post_init__(self) -> None:
        """Rejects a negative side.

        :raises InvalidInput: if height is below zero, or if width is
        below zero. Both failures are reported together.

        :return: nothing. A side of zero stays.
        """
        reasons: list[str] = []
        if self.height < 0:
            reasons.append(
                f"высота меньше 0, высота={self.height} мм",
            )
        if self.width < 0:
            reasons.append(
                f"ширина меньше 0, ширина={self.width} мм",
            )
        if reasons:
            raise InvalidInput(
                subject="Sheet",
                reason=reasons,
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
