"""A whole-number percent and the factors derived from it."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Percent:
    """
    Value Object. A whole-number percent of a price, and the factors derived from it.
    """

    value: int

    def factor(self) -> Decimal:
        """Returns one plus this percent.

        :return: 1 + value/100. Percent(30) returns 1.3. Percent(0)
        returns 1.
        """
        return Decimal(1) + Decimal(self.value) / Decimal(100)

    def compensation(self) -> Decimal:
        """Returns the gross-up that leaves this percent of the price.

        :return: 100/value. Percent(93) returns 100/93.
        """
        return Decimal(100) / Decimal(self.value)
