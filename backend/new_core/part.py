"""One printed part of a product: its target, count, and finishing."""

from dataclasses import dataclass

from backend.new_core.operations.run_operation import RunOperation
from backend.new_core.values.percent import Percent
from backend.new_core.errors import InvalidInput
from backend.new_core.materials.sheet import Sheet


@dataclass(frozen=True, slots=True)
class Part:
    """
    Value Object. One printed part: its target, copy count, markup, and finishing.
    """

    target: Sheet
    count: int
    markup: Percent
    operations: tuple[RunOperation, ...]

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
