from backend.aggregate.laminator.values.lamination import Lamination
from backend.workplace.reports import LaminationReport


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
