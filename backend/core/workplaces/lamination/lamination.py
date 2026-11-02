from backend.core.workplaces.lamination.models import LaminationReport, \
    Lamination


class LaminationWorkplace:
    def report(self, lamination: Lamination) -> LaminationReport:
        """Returns the number of film sides for one printing.

        :param lamination: ONE_ZERO or ONE_ONE.

        :raises ValueError: if there is no lamination,
        the value object's ValueError passes to the caller.

        :return: a LaminationReport. film_sides is the number of film sides.
        """
        return LaminationReport(film_sides=lamination.film_sides())
