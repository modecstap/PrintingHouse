from enum import Enum

from backend.workplace.reports import LaminationReport


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


class LaminationWorkplace:
    def report(self, lamination: Lamination) -> LaminationReport:
        """Возвращает число сторон плёнки для одной печати.

        Предусловие: lamination — ONE_ZERO или ONE_ONE.
        Число 200 и внутреннее число листов в метод не входят.
        Результат: LaminationReport. film_sides — число сторон плёнки.
        Ошибка: ValueError value object проходит к вызывающему,
        если ламинации нет.
        Побочные эффекты: нет.
        """
        return LaminationReport(film_sides=lamination.film_sides())
