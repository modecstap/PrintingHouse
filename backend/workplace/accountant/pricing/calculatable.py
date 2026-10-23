from abc import abstractmethod
from typing import Protocol

from backend.workplace.accountant.pricing.stage_cost import StageCost


class Calculatable(Protocol):
    @abstractmethod
    def calculate(self) -> StageCost:
        ...
