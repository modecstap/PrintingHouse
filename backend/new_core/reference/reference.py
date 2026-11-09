"""Named pointer to an exemplar customer order."""

from __future__ import annotations

from dataclasses import dataclass

from backend.new_core.order.order import OrderID


@dataclass(frozen=True, slots=True)
class Reference:
    """Value Object. A named exemplar order for templates or comparison."""

    name: str
    description: str
    order_id: OrderID
