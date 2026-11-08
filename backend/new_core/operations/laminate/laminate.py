"""One lamination of a press sheet."""

from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

from backend.new_core.materials.film import Film
from backend.new_core.operations.laminate.lamination import Lamination
from backend.new_core.values.money import Money

if TYPE_CHECKING:
    from backend.new_core.print_run.print_run import PrintRun
from backend.new_core.equipment.laminator import Laminator
from backend.new_core.personal.laminator_operator import LaminatorOperator


@dataclass(frozen=True, slots=True)
class Laminate:
    """
    Value Object. One lamination of a press sheet: the specification,
    the laminator, and the operator.
    """

    laminator: Laminator
    operator: LaminatorOperator
    lamination: Lamination
    film: Film

    def material_price(self, run: PrintRun) -> Money:
        """Returns the film cost of one press sheet.

        :return: zero when the lamination has no film sides. Otherwise, the
        film price times the number of sides. Film density is not read.
        """
        sides = self.lamination.film_sides()
        if sides == 0:
            return Money.zero()
        return self.film.price * sides

    def work_price(self, run: PrintRun) -> Money:
        """Returns the laminator operator salary for one press sheet.

        :return: zero when the lamination has no film sides. Otherwise, the
        full salary once, including when the film covers two sides.
        """
        if self.lamination.film_sides() == 0:
            return Money.zero()
        return self.operator.salary_by_operation

    def startup_price(self, run: PrintRun) -> Money:
        """Returns the laminator startup for the operation.

        :return: zero when the lamination has no film sides. Otherwise, the
        laminator startup. The press sheet count does not divide it.
        """
        if self.lamination.film_sides() == 0:
            return Money.zero()
        return self.laminator.startup
