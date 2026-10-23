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
        """Возвращает число сторон плёнки.

        Результат: 1, если плёнка с одной стороны, и 2, если с двух.
        Ошибка: ValueError, если ламинации нет.
        """
        if self is Lamination.DONT:
            return 0
        if self is Lamination.ONE_ZERO:
            return 1
        if self is Lamination.ONE_ONE:
            return 2
        raise ValueError(f"число сторон плёнки: {self!r}")
