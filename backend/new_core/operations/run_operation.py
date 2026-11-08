from typing import Protocol

from backend.new_core.values.money import Money


class RunOperation(Protocol):
    def material_price(self) -> Money:
        """Returns the material cost of one press sheet.

        :return: the material money for one press sheet.
        Startup is not included.
        """
        ...

    def work_price(self) -> Money:
        """Returns the work cost of one press sheet.

        :return: the work money for one press sheet.
        Startup is not included.
        """
        ...

    def startup_price(self) -> Money:
        """Returns the startup cost of the operation.

        :return: the startup money for the whole operation.
        The press sheet count does not divide it.
        """
        ...
