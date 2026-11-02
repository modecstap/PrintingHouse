from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class LaminationReport:
    film_sides: int

class Lamination(Enum):
    DONT = 1
    ONE_ZERO = 2
    ONE_ONE = 3

    def film_sides(self) -> int:
        """Returns the number of film sides.

        :raises ValueError: if there is no lamination.

        :return: 1 if the film is on one side, and 2 if it is on two sides.
        """
        if self is Lamination.DONT:
            return 0
        if self is Lamination.ONE_ZERO:
            return 1
        if self is Lamination.ONE_ONE:
            return 2
        raise ValueError(f"число сторон плёнки: {self!r}")
