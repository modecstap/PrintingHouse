"""The priced product, the priced order, and the income."""

from dataclasses import dataclass

from backend.core.accountant.money import Money


@dataclass(frozen=True)
class OrderReport:
    """Product price, order price, income, and imposition counts."""

    product_price: Money
    order_price: Money
    income: Money
    impositions: tuple[int, ...]
