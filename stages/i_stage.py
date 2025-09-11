from abc import ABC, abstractmethod
from decimal import Decimal


class IStage(ABC):
    @abstractmethod
    def get_cost(self) -> Decimal:
        pass

    @abstractmethod
    def get_cost_price(self) -> Decimal:
        pass
