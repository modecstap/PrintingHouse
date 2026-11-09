from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.order.product import Product


@dataclass(frozen=True, slots=True)
class OrderID:
    """Value Object. Stable identifier of a customer order."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidInput(
                "order id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True)
class Order:
    id: OrderID
    product: Product
    count: int

    def __post_init__(self) -> None:
        """Rejects a negative order count.

        :raises InvalidInput: if count is below zero.

        :return: nothing. A count of zero stays.
        """
        if self.count < 0:
            raise InvalidInput(
                "order",
                f"количество меньше 0, количество={self.count}",
            )
