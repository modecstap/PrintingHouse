"""A whole-number percent and the factors derived from it."""

from dataclasses import dataclass
from decimal import Decimal


__all__ = ["Percent"]

@dataclass(frozen=True, slots=True)
class Percent:
    """Value Object. A whole-number percent of a price,
    and the factors derived from it.
    """

    value: int

    def factor(self) -> Decimal:
        """Returns one plus this percent.

        :return: the Decimal result.
        """
        return Decimal(1) + Decimal(self.value) / Decimal(100)

    def compensation(self) -> Decimal:
        """Returns the gross-up that leaves this percent of the price.

        :return: the Decimal result.
        """
        return Decimal(100) / Decimal(self.value)
