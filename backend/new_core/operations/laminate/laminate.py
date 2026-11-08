"""One lamination of a press sheet."""

from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.new_core.operations.laminate.laminator import Laminator
from backend.new_core.operations.laminate.laminator_operator import LaminatorOperator
from backend.new_core.operations.laminate.lamination_specification import (
    LaminationSpecification,
)


@dataclass(frozen=True, slots=True)
class Laminate:
    """
    Value Object. One lamination of a press sheet: the specification,
    the laminator, and the operator.
    """

    spec: LaminationSpecification
    laminator: Laminator
    operator: LaminatorOperator

    def material_price(self) -> Money:
        """Returns the film cost of one press sheet.

        :return: zero when the lamination has no film sides. Otherwise, the
        film price times the number of sides. Film density is not read.
        """
        sides = self.spec.film_sides()
        if sides == 0:
            return Money.zero()
        return self.spec.film.price * sides

    def work_price(self) -> Money:
        """Returns the laminator operator salary for one press sheet.

        :return: zero when the lamination has no film sides. Otherwise, the
        full salary once, including when the film covers two sides.
        """
        if self.spec.film_sides() == 0:
            return Money.zero()
        return self.operator.salary_by_operation

    def startup_price(self) -> Money:
        """Returns the laminator startup for the operation.

        :return: zero when the lamination has no film sides. Otherwise, the
        laminator startup. The press sheet count does not divide it.
        """
        if self.spec.film_sides() == 0:
            return Money.zero()
        return self.laminator.startup
