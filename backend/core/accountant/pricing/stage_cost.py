from dataclasses import dataclass

from backend.core.accountant.money import Money


@dataclass(frozen=True)
class StageCost:
    startup_cost: Money
    material_cost: Money
    salary: Money

    @classmethod
    def zero(cls) -> "StageCost":
        """Returns zero startup, zero material, and zero salary."""
        return cls(
            startup_cost=Money.zero(),
            material_cost=Money.zero(),
            salary=Money.zero(),
        )
