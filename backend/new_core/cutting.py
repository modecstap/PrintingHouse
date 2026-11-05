from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.new_core.errors import InvalidInput


@dataclass(frozen=True)
class Cutter:
    id: int
    max_stack: int

    def __post_init__(self) -> None:
        """Rejects a negative stack height.

        :raises InvalidInput: if max_stack is below zero.

        :return: nothing. A stack height of zero stays.
        """
        if self.max_stack < 0:
            raise InvalidInput(
                "cutter",
                f"высота стопы меньше 0, высота={self.max_stack} мм",
            )


@dataclass(frozen=True)
class CutterOperator:
    id: int
    salary_by_operation: Money
