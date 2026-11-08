from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from backend.new_core.values.money import Money

if TYPE_CHECKING:
    from backend.new_core.print_run.print_run import PrintRun


class RunOperation(Protocol):
    def material_price(self, run: PrintRun) -> Money:
        """Returns the material cost of one press sheet.

        :return: the material money for one press sheet.
        Startup is not included.
        """
        ...

    def work_price(self, run: PrintRun) -> Money:
        """Returns the work cost of one press sheet.

        :return: the work money for one press sheet.
        Startup is not included.
        """
        ...

    def startup_price(self, run: PrintRun) -> Money:
        """Returns the startup cost of the operation.

        :return: the startup money for the whole operation.
        The press sheet count does not divide it.
        """
        ...
