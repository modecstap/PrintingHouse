"""The blocks and the additional work that make one product."""

from dataclasses import dataclass

from backend.new_core.order.additional_work import AdditionalWork
from backend.new_core.part import Part


@dataclass(frozen=True, slots=True)
class Product:
    """
    Value Object. The parts and the additional work priced together as one product.
    """

    blocks: tuple[Part, ...]
    operations: tuple[AdditionalWork, ...]
