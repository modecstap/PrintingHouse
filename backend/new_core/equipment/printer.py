"""A printer: its startup and the price of each ink."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.values.money import Money


@dataclass(frozen=True, slots=True)
class PrinterID:
    """Value Object. Stable identifier of a printer in the equipment catalog."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidInput(
                "printer id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True)
class Printer:
    """A printer: its startup and the price of each ink."""

    id: PrinterID
    startup: Money
    cyan: Money
    magenta: Money
    yellow: Money
    black: Money
