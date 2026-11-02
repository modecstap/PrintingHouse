import math

from backend.core.workplaces.cutting.models import CuttingReport


class CuttingWorkplace:
    def report(
        self,
        internal_sheet_count: int,
        stack_height: int,
        density: int,
        cut_count: int,
    ) -> CuttingReport:
        """Returns the number of human cuts for one printing.

        :param internal_sheet_count: the internal sheet count, including fitting.
        :param stack_height: the cutter stack height.
        :param density: the paper density in grams per square meter.
        :param cut_count: the number of layout cuts.

        :return: a CuttingReport. human_cuts is the number of human cuts.
        The charge for cuts is not divided by the sheet count.
        """
        sheet_in_stack = max(math.ceil(stack_height * 1200 / density), 0)
        human_cuts = math.ceil(internal_sheet_count / sheet_in_stack) * cut_count
        return CuttingReport(human_cuts=human_cuts)
