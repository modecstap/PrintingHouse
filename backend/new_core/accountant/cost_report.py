"""A price split into material, startup, work, and markup."""

from dataclasses import dataclass
from decimal import Decimal

from backend.core.accountant.money import Money
from backend.new_core.accountant.percent import Percent


@dataclass(frozen=True)
class CostReport:
    """Material, startup, work, and the markup added on top of them."""

    material: Money
    startup: Money
    work: Money
    markup: Money

    def apply_markup(self, percent: Percent) -> "CostReport":
        """Adds a percent of material, startup, and work to markup.

        :param percent: the percent to add. Zero adds nothing.
        Markup already stored is kept and is not scaled.

        :return: the same material, startup, and work. The markup is
        (material + startup + work) * (factor - 1) plus the stored markup.
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

        :return: the sum of the four amounts.
        """
        return self.material + self.startup + self.work + self.markup

    def cost_price(self) -> Money:
        """Returns material and startup, without work or markup.

        :return: the sum of material and startup.
        """
        return self.material + self.startup

    @classmethod
    def zero(cls) -> "CostReport":
        """Returns a report whose four amounts are zero.

        :return: material, startup, work, and markup, each zero.
        """
        return cls(
            material=Money.zero(),
            startup=Money.zero(),
            work=Money.zero(),
            markup=Money.zero(),
        )

    def __mul__(self, other):
        if isinstance(other, (int, float, Decimal)):
            return CostReport(
                material=self.material * other,
                startup=self.startup * other,
                work=self.work * other,
                markup=self.markup * other,
            )
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, CostReport):
            return CostReport(
                material=self.material + other.material,
                startup=self.startup + other.startup,
                work=self.work + other.work,
                markup=self.markup + other.markup,
            )
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return CostReport(
                material=self.material / other,
                startup=self.startup / other,
                work=self.work / other,
                markup=self.markup / other,
            )
        return NotImplemented
