from dataclasses import dataclass

from backend.core.workplaces.printing.models import Chroma
from backend.new_core import InvalidInput, Sheet
from backend.new_core.operations.lamination import LaminationSpecification


@dataclass(frozen=True)
class Block:
    sheet: Sheet
    count: int

    chroma: Chroma
    lamination: LaminationSpecification
    die_cutting: bool

    def __post_init__(self) -> None:
        """Rejects a negative block count.

        :raises InvalidInput: if count is below zero.

        :return: nothing. A count of zero stays.
        """
        if self.count < 0:
            raise InvalidInput(
                "block",
                f"количество меньше 0, количество={self.count}",
            )
