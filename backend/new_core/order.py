from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.new_core.errors import InvalidInput
from backend.new_core.sheet import Sheet


@dataclass(frozen=True)
class Operation:
    name: str
    price: Money
    description: str


@dataclass(frozen=True)
class Block:
    sheet: Sheet
    count: int

    def __post_init__(self) -> None:
        """Rejects a negative block count.

        :raises InvalidInput: if count is below zero.

        :return: nothing. A count of zero stays.
        """
        if self.count < 0:
            raise InvalidInput(
                "block",
                f"количество меньше 0, количество={self.count}",
            )


@dataclass(frozen=True)
class Product:
    blocks: tuple[Block, ...]
    operations: tuple[Operation, ...]


@dataclass(frozen=True)
class Order:
    id: int
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
