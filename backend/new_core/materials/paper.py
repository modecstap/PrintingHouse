"""One paper grade: density, thickness, name, and price."""

from dataclasses import dataclass
from decimal import Decimal

from backend.new_core.values.money import Money
from backend.new_core.errors import InvalidInput


@dataclass(frozen=True, slots=True)
class Paper:
    """
    Value Object. The density, the thickness, the name, and the price of one kilogram of a paper grade.
    """

    density: int
    thickness: Decimal
    name: str
    price_per_kilo: Money

    def __post_init__(self) -> None:
        """Rejects invalid density or thickness.

        :raises InvalidInput: if density is below one, if thickness is not a
        positive Decimal with at most two fractional digits. Both failures are
        reported together.

        :return: nothing. A negative price never reaches this method,
        because Money rejects it first.
        """
        reasons: list[str] = []
        if self.density <= 0:
            reasons.append(
                f"плотность бумаги меньше или равна 0, плотность={self.density} г/м²",
            )
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
