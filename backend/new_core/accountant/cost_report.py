"""A price split into material, startup, work, and markup."""

from dataclasses import dataclass
from decimal import Decimal

from backend.new_core.values.money import Money
from backend.new_core.values.percent import Percent


__all__ = ["CostReport"]

@dataclass(frozen=True, slots=True)
class CostReport:
    """Value Object. A price split into material, startup, work,
    and the markup added on top.
    """

    material: Money
    startup: Money
    work: Money
    markup: Money

    def apply_markup(self, percent: Percent) -> "CostReport":
        """Adds a percent of material, startup, and work to markup.

        :param percent: the percent to add. Zero adds nothing.

        :return: the 'CostReport' result.
        """
        base = self.material + self.startup + self.work
        added = base * (percent.factor() - 1)
        return CostReport(
            material=self.material,
            startup=self.startup,
            work=self.work,
            markup=added + self.markup,
        )

    def total(self) -> Money:
        """Returns material, startup, work, and markup added together.

        :return: the Money result.
        """
        return self.material + self.startup + self.work + self.markup

    def cost_price(self) -> Money:
        """Returns material and startup, without work or markup.

        :return: the Money result.
        """
        return self.material + self.startup

    @classmethod
    def zero(cls) -> "CostReport":
        """Returns a report whose four amounts are zero.

        :return: the 'CostReport' result.
        """
        return cls(
            material=Money.zero(),
            startup=Money.zero(),
            work=Money.zero(),
            markup=Money.zero(),
        )

    def __mul__(self, other: object) -> "CostReport | type[NotImplemented]":
        """Multiplies by a factor.

        :param other: numeric factor.

        :return: the 'CostReport | type[NotImplemented]' result.
        """
        if isinstance(other, (int, float, Decimal)):
            return CostReport(
                material=self.material * other,
                startup=self.startup * other,
                work=self.work * other,
                markup=self.markup * other,
            )
        return NotImplemented

    def __add__(
        self, other: object
    ) -> "CostReport | type[NotImplemented]":
        """Adds another operand.

        :param other: another cost report.

        :return: the 'CostReport | type[NotImplemented]' result.
        """
        if isinstance(other, CostReport):
            return CostReport(
                material=self.material + other.material,
                startup=self.startup + other.startup,
                work=self.work + other.work,
                markup=self.markup + other.markup,
            )
        return NotImplemented

    def __truediv__(
        self, other: object
    ) -> "CostReport | type[NotImplemented]":
        """Divides by a divisor.

        :param other: numeric divisor.

        :return: the 'CostReport | type[NotImplemented]' result.
        """
        if isinstance(other, (int, float)):
            return CostReport(
                material=self.material / other,
                startup=self.startup / other,
                work=self.work / other,
                markup=self.markup / other,
            )
        return NotImplemented
