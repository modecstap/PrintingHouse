"""Print run persistence contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.order.order import OrderID
from backend.new_core.print_run.print_run import PrintRun, PrintRunID


__all__ = ["PrintRunRepository"]

class PrintRunRepository(Protocol):
    """Loads and stores print runs for an order."""

    def take_all_for_order(self, order_id: OrderID) -> tuple[PrintRun, ...]:
        """Returns every print run linked to the order.

        :param order_id: id of the order.
"""
        ...

    def generate_id(self, order_id: OrderID) -> PrintRunID:
        """Returns the next print run id for this order.

        :param order_id: scopes the id sequence.
"""
        ...

    def save_all_for_order(
        self,
        order_id: OrderID,
        runs: tuple[PrintRun, ...],
    ) -> None:
        """Replaces all print runs linked to the order.

        :param order_id:
        :param runs:

        :raises ValueError: if a run's for_order is not order_id.
        """
        ...
