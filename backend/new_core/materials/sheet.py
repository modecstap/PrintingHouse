"""One press sheet: its paper grade and its format."""

from dataclasses import dataclass
from decimal import Decimal

from backend.new_core.errors import InvalidInput
from backend.new_core.values.money import Money
from backend.new_core.materials.paper import Paper
from backend.new_core.format import Format


__all__ = [
    "SheetID",
    "Sheet",
]

@dataclass(frozen=True, slots=True)
class SheetID:
    """Value Object. Stable identifier of a sheet in the materials catalog."""

    value: int

    def __post_init__(self) -> None:
        """Validates fields after construction.

        :raises InvalidInput: when the operation fails.
        """
        if self.value < 0:
            raise InvalidInput(
                "sheet id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True, slots=True)
class Sheet:
    """Entity. One sheet row in the materials catalog.

    Paper grade and format stay nested on the entity.
    """

    id: SheetID
    paper: Paper
    format: Format

    def mass_kg(self) -> Decimal:
        """Returns the mass of one sheet in kilograms.

        :return: the Decimal result.
        """
        return (
            Decimal(self.format.width)
            * Decimal(self.format.height)
            / Decimal(1_000_000)
            * Decimal(self.paper.density.value)
            / Decimal(1000)
        )

    def thickness(self) -> Decimal:
        """Returns the thickness of the sheet.

        :return: the Decimal result.
        """
        return self.paper.thickness

    def price(self) -> Money:
        """Returns the price of one sheet.

        :return: the Money result.
        """
        return self.paper.price_per_kilo * self.mass_kg()
