"""One paper grade: density, thickness, name, and price."""

from dataclasses import dataclass

from backend.new_core.values.money import Money
from backend.new_core.errors import InvalidInput


@dataclass(frozen=True, slots=True)
class Paper:
    """
    Value Object. The density, the thickness, the name, and the price of one kilogram of a paper grade.
    """

    density: int
    thickness: int
    name: str
    price_per_kilo: Money

    def __post_init__(self) -> None:
        """Rejects a density or a thickness that is not positive.

        :raises InvalidInput: if density is below one, or if thickness is
        below one. Both failures are reported together.

        :return: nothing. A negative price never reaches this method,
        because Money rejects it first.
        """
        reasons: list[str] = []
        if self.density <= 0:
            reasons.append(
                f"плотность бумаги меньше или равна 0, плотность={self.density} г/м²",
            )
        if self.thickness <= 0:
            reasons.append(
                f"толщина бумаги меньше или равна 0, толщина={self.thickness} мм",
            )
        if reasons:
            raise InvalidInput(
                subject="Paper",
                reason=reasons,
            )
