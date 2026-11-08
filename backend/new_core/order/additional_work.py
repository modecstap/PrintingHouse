"""Named extra work on a product, with its price and markup."""

from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.new_core.accountant.percent import Percent


@dataclass(frozen=True, slots=True)
class AdditionalWork:
    """
    Value Object. One extra job on a product: its name, price, description, and markup.
    """

    name: str
    price: Money
    description: str
    markup: Percent
