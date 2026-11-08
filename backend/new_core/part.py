"""One printed part of a product: its sheet, count, and finishing."""

from dataclasses import dataclass

from backend.core.workplaces.printing.models import Chroma
from backend.new_core.accountant.percent import Percent
from backend.new_core.errors import InvalidInput
from backend.new_core.sheet import Sheet
from backend.new_core.operations.lamination import LaminationSpecification


@dataclass(frozen=True, slots=True)
class Part:
    """
    Value Object. One printed part: its sheet, copy count, markup, and finishing.
    """

    sheet: Sheet
    count: int
    markup: Percent

    chroma: Chroma
    lamination: LaminationSpecification
    die_cutting: bool

    def __post_init__(self) -> None:
        """Rejects a negative block count.

        :raises InvalidInput: if count is below zero.

        :return: nothing. A count of zero stays.
        """
        reasons: list[str] = []
        if self.count < 0:
            reasons.append(
                f"количество меньше 0, количество={self.count}",
            )
        if reasons:
            raise InvalidInput(
                subject="Part",
                reason=reasons,
            )
