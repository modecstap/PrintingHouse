from dataclasses import dataclass

from backend.workplace.accountant.money import Money


@dataclass(frozen=True)
class StageCost:
    startup_cost: Money
    material_cost: Money
    salary: Money

    @classmethod
    def zero(cls) -> "StageCost":
        """Возвращает нулевой запуск, нулевой материал и нулевую зарплату.

        Побочные эффекты: нет.
        """
        return cls(
            startup_cost=Money.zero(),
            material_cost=Money.zero(),
            salary=Money.zero(),
        )
