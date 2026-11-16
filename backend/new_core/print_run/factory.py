"""Builds print runs with ids from the store."""

from backend.new_core.order.order import OrderID
from backend.new_core.part import Part
from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.print_run.repository import PrintRunRepository


__all__ = ["PrintRunFactory"]

class PrintRunFactory:
    """Allocates print run ids and builds runs."""

    def __init__(self, print_runs: PrintRunRepository) -> None:
        """Initializes this instance.

        :param print_runs: the print runs.
        """
        self._print_runs = print_runs

    def create(
        self,
        for_order: OrderID,
        block: Part,
        required_count: int,
    ) -> PrintRun:
        """Builds a print run with a generated id.

        :param for_order: the for order.
        :param block: the block.
        :param required_count: the required count.

        :return: the PrintRun result.
        """
        return PrintRun(
            id=self._print_runs.generate_id(for_order),
            for_order=for_order,
            block=block,
            required_count=required_count,
        )
