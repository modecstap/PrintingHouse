from typing import Protocol

from backend.workplace.accountant.pricing.stage_cost import StageCost


class Calculatable(Protocol):
    def calculate(self) -> StageCost:
        ...
