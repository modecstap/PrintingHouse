"""One paper grade: density, thickness, type, and price."""

from dataclasses import dataclass
from decimal import Decimal

from backend.new_core.materials.paper_density import PaperDensity
from backend.new_core.materials.paper_type import PaperType
from backend.new_core.values.money import Money
from backend.new_core.errors import InvalidInput


@dataclass(frozen=True, slots=True)
class Paper:
    """
    Value Object. The density, the thickness, the paper type, and the price
    of one kilogram of a paper grade.
    """

    density: PaperDensity
    thickness: Decimal
    type: PaperType
    price_per_kilo: Money

    def __post_init__(self) -> None:
        """Rejects invalid thickness.

        :raises InvalidInput: if thickness is not a positive Decimal with at
        most two fractional digits.

        :return: nothing. A negative price never reaches this method,
        because Money rejects it first.
        """
        reasons: list[str] = []
        if type(self.thickness) is not Decimal:
            reasons.append(
                f"толщина бумаги должна быть Decimal, толщина={self.thickness!r}",
            )
        elif self.thickness <= 0:
            reasons.append(
                f"толщина бумаги меньше или равна 0, толщина={self.thickness} мм",
            )
        elif self.thickness != self.thickness.quantize(Decimal("0.01")):
            reasons.append(
                f"толщина бумаги имеет более 2 знаков после запятой, "
                f"толщина={self.thickness} мм",
            )
        if reasons:
            raise InvalidInput(
                subject="Paper",
                reason=reasons,
            )
