from backend.core.workplaces.die_cutting.models import DieCuttingReport


class DieCuttingWorkplace:
    def report(self, sheet_count: int, die_cutting: bool) -> DieCuttingReport:
        """Returns the item sheet count for the die-cutting charge.

        :param sheet_count: the sheet count without fitting,
        already calculated by the administrator.
        :param die_cutting:

        :return: a DieCuttingReport with the same sheet_count.
        The sheet count is not multiplied by the die-cutting rate.
        """
        if not die_cutting:
            return DieCuttingReport(0)
        return DieCuttingReport(sheet_count=sheet_count)
