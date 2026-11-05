from dataclasses import dataclass

from backend.core.order import Operation
from backend.new_core.order.block import Block


@dataclass(frozen=True)
class Product:
    blocks: tuple[Block, ...]
    operations: tuple[Operation, ...]