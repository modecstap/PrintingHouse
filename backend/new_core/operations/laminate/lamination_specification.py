"""Which lamination a part uses, and the film that lamination applies."""

from dataclasses import dataclass

from backend.core.workplaces.lamination.models import Lamination
from backend.new_core.operations.laminate.film import Film


@dataclass(frozen=True, slots=True)
class LaminationSpecification:
    """
    Value Object. Which lamination a part uses, and the film that lamination applies.
    """

    lamination: Lamination
    film: Film

    def film_sides(self) -> int:
        """Returns how many sides of this lamination receive film.

        :return: the number of sides of the lamination that have film.
        """
        return self.lamination.film_sides()
