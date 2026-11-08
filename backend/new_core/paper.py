"""One paper grade: density, thickness, name, and price."""

from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.new_core.errors import InvalidInput


@dataclass(frozen=True)
class Paper:
    """The density, the thickness, the name, and the price of one kilogram."""

    density: int
    thickness: int
    name: str
    price_per_kilo: Money

    def __post_init__(self) -> None:
        """Rejects a density or a thickness that is not positive.

        :raises InvalidInput: if density is below one, or if thickness is
        below one after density is accepted.

        :return: nothing. A negative price never reaches this method,
        because Money rejects it first.
        """
        if self.density <= 0:
            raise InvalidInput(
                "paper",
                f"плотность бумаги меньше или равна 0, плотность={self.density} г/м²",
            )
        if self.thickness <= 0:
            raise InvalidInput(
                "paper",
                f"толщина бумаги меньше или равна 0, толщина={self.thickness} мм",
            )
