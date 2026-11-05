from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.new_core.press_job import PressJob


@dataclass(frozen=True)
class DieCutterOperator:
    id: int
    salary_by_operation: Money


@dataclass(frozen=True)
class DieCut:
    operator: DieCutterOperator

    def material_price(self, job: PressJob) -> Money:
        """Returns no material for a die cut.

        :param job: present for the shared operation signature. It is not used.

        :return: zero.
        """
        return Money.zero()

    def work_price(self, job: PressJob) -> Money:
        """Returns the die cutter salary for one press sheet.

        :param job: present for the shared operation signature. It is not used.

        :return: the full salary.
        """
        return self.operator.salary_by_operation

    def startup_price(self, job: PressJob) -> Money:
        """Returns no startup for a die cut.

        :param job: present for the shared operation signature. It is not used.

        :return: zero.
        """
        return Money.zero()

