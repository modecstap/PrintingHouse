from dataclasses import dataclass

from backend.core.accountant.money import Money


@dataclass(frozen=True)
class CostReport:
    material: Money
    startup: Money
    work: Money

    def total(self) -> Money:
        return self.material + self.startup + self.work

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return CostReport(
                material=self.material * other,
                startup=self.startup * other,
                work=self.work * other,
            )
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, CostReport):
            return CostReport(
                material=self.material + other.material,
                startup=self.startup + other.startup,
                work=self.work + other.work,
            )
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return CostReport(
                material=self.material / other,
                startup=self.startup / other,
                work=self.work / other,
            )
        return NotImplemented