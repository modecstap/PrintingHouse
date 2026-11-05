from dataclasses import dataclass

from backend.core.accountant.money import Money


@dataclass(frozen=True)
class Operation:
    name: str
    price: Money
    description: str
