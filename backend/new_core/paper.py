from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.new_core.errors import InvalidInput


@dataclass(frozen=True)
class Paper:
    density: int
    name: str
    price_per_kilo: Money

    def __post_init__(self) -> None:
        """Rejects a density that is not positive.

        :raises InvalidInput: if density is below one.

        :return: nothing. A negative price never reaches this method,
        because Money rejects it first.
        """
        if self.density <= 0:
            raise InvalidInput(
                "paper",
                f"плотность бумаги меньше или равна 0, плотность={self.density} г/м²",
            )
