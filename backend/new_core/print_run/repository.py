"""Print run persistence contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.order.order import OrderID
from backend.new_core.print_run.print_run import PrintRun


class PrintRunRepository(Protocol):
    """Loads print runs for an order."""

    def take_all_for_order(self, order_id: OrderID) -> tuple[PrintRun, ...]:
        """Returns every print run linked to the order.

        :param order_id:

        :return: runs in repository order. No runs: an empty tuple.
        """
        ...
