from dataclasses import dataclass
from typing import Protocol

from backend.core.accountant.money import Money
from backend.new_core.sheet import Sheet


@dataclass(frozen=True)
class PressJob:
    press_sheet_count: int
    cut_count: int
    press_sheet: Sheet


class RunOperation(Protocol):
    def material_price(self, job: PressJob) -> Money:
        """Returns the material cost of one press sheet.

        :param job: the priced press run.

        :return: the material money for one press sheet.
        Startup is not included.
        """
        ...

    def work_price(self, job: PressJob) -> Money:
        """Returns the work cost of one press sheet.

        :param job: the priced press run.

        :return: the work money for one press sheet.
        Startup is not included.
        """
        ...

    def startup_price(self, job: PressJob) -> Money:
        """Returns the startup cost of one press sheet.

        :param job: the priced press run.

        :return: the startup money for one press sheet.
        """
        ...
