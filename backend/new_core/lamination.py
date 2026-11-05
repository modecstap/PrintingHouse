from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.core.workplaces.lamination.models import Lamination
from backend.new_core.press_job import PressJob


@dataclass(frozen=True)
class Film:
    """A film name and its price.

    Density does not change the money of a run.
    The constructor does not check the sign of density.
    """

    name: str
    price: Money
    density: int


@dataclass(frozen=True)
class Laminator:
    id: int
    startup: Money


@dataclass(frozen=True)
class LaminatorOperator:
    id: int
    salary_by_operation: Money


@dataclass(frozen=True)
class Laminate:
    lamination: Lamination
    laminator: Laminator
    film: Film
    operator: LaminatorOperator

    def material_price(self, job: PressJob) -> Money:
        """Returns the film cost of one press sheet.

        :param job: present for the shared operation signature. It is not used.

        :return: zero when the lamination has no film sides. Otherwise the
        film price times the number of sides. Film density is not read.
        """
        sides = self.lamination.film_sides()
        if sides == 0:
            return Money.zero()
        return self.film.price * sides

    def work_price(self, job: PressJob) -> Money:
        """Returns the laminator operator salary for one press sheet.

        :param job: present for the shared operation signature. It is not used.

        :return: zero when the lamination has no film sides. Otherwise the
        full salary once, including when the film covers two sides.
        """
        if self.lamination.film_sides() == 0:
            return Money.zero()
        return self.operator.salary_by_operation

    def startup_price(self, job: PressJob) -> Money:
        """Returns the laminator startup spread over the press sheets.

        :param job: the run whose press sheet count divides the startup.
        The count is already positive.

        :return: zero when the lamination has no film sides. Otherwise the
        laminator startup divided by the press sheet count.
        """
        if self.lamination.film_sides() == 0:
            return Money.zero()
        return self.laminator.startup / job.press_sheet_count

