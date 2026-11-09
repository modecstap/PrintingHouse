"""One press sheet: its paper grade and its format."""

from dataclasses import dataclass
from decimal import Decimal

from backend.new_core.errors import InvalidInput
from backend.new_core.values.money import Money
from backend.new_core.materials.paper import Paper
from backend.new_core.format import Format


@dataclass(frozen=True, slots=True)
class SheetID:
    """Value Object. Stable identifier of a sheet in the materials catalog."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidInput(
                "sheet id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True, slots=True)
class Sheet:
    """
    Entity. One sheet row in the materials catalog.

    Paper grade and format stay nested on the entity.
    """

    id: SheetID
    paper: Paper
    format: Format

    def mass_kg(self) -> Decimal:
        """Returns the mass of one sheet in kilograms.

        :return: width times height, divided by 1_000_000, times the paper
        density, divided by 1000. Every factor is a Decimal.
        """
        return (
            Decimal(self.format.width)
            * Decimal(self.format.height)
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
