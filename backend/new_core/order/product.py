"""The blocks and the additional work that make one product."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.order.additional_work import AdditionalWork
from backend.new_core.part import Part
from backend.new_core.values.percent import Percent


@dataclass(frozen=True, slots=True)
class Product:
    """
    Value Object. The parts and the additional work priced together as one product.
    """

    parts_markup: Percent
    blocks: tuple[Part, ...]
    operations: tuple[AdditionalWork, ...]

    def __post_init__(self) -> None:
        """Rejects a product with no blocks.

        :raises InvalidInput: if blocks is empty.

        :return: nothing.
        """
        if not self.blocks:
            raise InvalidInput(
                subject="Product",
                reason="нет блоков продукта",
            )
