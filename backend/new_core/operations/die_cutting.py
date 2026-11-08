from dataclasses import dataclass

from backend.core.accountant.money import Money


@dataclass(frozen=True)
class DieCutterOperator:
    id: int
    salary_by_operation: Money


@dataclass(frozen=True, slots=True)
class DieCut:
    """
    Value Object. One die cut of a press sheet, priced from the operator salary.
    """

    operator: DieCutterOperator

    @staticmethod
    def material_price() -> Money:
        """Returns no material for a die cut.

        :return: zero.
        """
        return Money.zero()

    def work_price(self) -> Money:
        """Returns the die cutter salary for one press sheet.

        :return: the full salary.
        """
        return self.operator.salary_by_operation

    @staticmethod
    def startup_price() -> Money:
        """Returns no startup for a die cut.

        :return: zero.
        """
        return Money.zero()

