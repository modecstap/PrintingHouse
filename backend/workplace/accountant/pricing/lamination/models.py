from dataclasses import dataclass

from backend.workplace.accountant.money import Money


@dataclass(frozen=True)
class LaminationPricing:
    startup: Money
    film_cost: Money
    salary: Money