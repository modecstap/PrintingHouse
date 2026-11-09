"""One press run for a block, and the operations appended to it."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

from backend.new_core.values.percent import Percent
from backend.new_core.part import Part
from backend.new_core.errors import InvalidInput
from backend.new_core.order.order import OrderID


@dataclass(frozen=True, slots=True)
class PrintRunID:
    """Value Object. Stable identifier of one press run."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidInput(
                "print run id",
                f"id меньше 0, id={self.value}",
            )


_WASTE_ALLOWANCE = Percent(3)


class PrintRun:
    """A run that prints one block and records the operations it uses."""

    def __init__(
            self,
            id: PrintRunID,  # pylint: disable=redefined-builtin
            for_order: OrderID,
            block: Part,
            required_count: int,
    ) -> None:
        self.id = id
        self.for_order = for_order
        self.block = block
        self.required_count = required_count

        if self.required_count < 0:
            raise InvalidInput(
                "print_run",
                f"необходимое количество меньше 0, количество={self.required_count}",
            )

        if self.imposition_count() <= 0:
            raise InvalidInput(
                "print_run",
                "печатных листов 0, "
                f"необходимое количество={self.required_count}",
            )

    def production_count(self) -> int:
        """Returns how many target sheets the run produces.

        :return: the press sheet count times the sheets on one press sheet.
        """
        return self.imposition_count() * self.block.imposition.count()

    def imposition_count(self) -> int:
        """Returns how many press sheets the run prints.

        :raises InvalidInput: if a cell side is zero, or if the press sheet
        fits no positive number of target sheets.

        :return: required_count times a 3 percent waste allowance, divided
        by the number of target sheets on one press sheet, rounded up
        to an integer.
        """
        sheets = (
                Decimal(self.required_count)
                * _WASTE_ALLOWANCE.factor()
                / Decimal(self.block.imposition.count())
        ).to_integral_value(rounding=ROUND_CEILING)
        return int(sheets)
