"""The priced product, the priced order, and the income."""

from dataclasses import dataclass

from backend.new_core.values.money import Money


__all__ = ["OrderReport"]

@dataclass(frozen=True, slots=True)
class OrderReport:
    """
    Value Object. The priced product, the priced order, the income,
    and the imposition counts.
    """

    product_price: Money
    order_price: Money
    income: Money
    impositions: tuple[int, ...]
