"""A printer: its startup and the price of each ink."""

from dataclasses import dataclass

from backend.new_core.errors import InvalidInput
from backend.new_core.values.money import Money


__all__ = [
    "PrinterID",
    "PrinterPrices",
    "Printer",
]

@dataclass(frozen=True, slots=True)
class PrinterID:
    """Value Object. Stable identifier of a printer in the equipment catalog."""

    value: int

    def __post_init__(self) -> None:
        """Validates fields after construction.

        :raises InvalidInput: when the operation fails.
        """
        if self.value < 0:
            raise InvalidInput(
                "printer id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True)
class PrinterPrices:  # pylint: disable=too-few-public-methods
    """Ink startup and per-channel prices; the fields are the value."""

    startup: Money
    cyan: Money
    magenta: Money
    yellow: Money
    black: Money


@dataclass(frozen=True)
class Printer:
    """A printer: its startup and the price of each ink."""

    id: PrinterID
    name: str
    spacing: int
    prices: PrinterPrices

    def __post_init__(self) -> None:
        """Validates fields after construction.

        :raises InvalidInput: when the operation fails.
        """
        stripped = self.name.strip()
        if not stripped:
            raise InvalidInput(
                subject="printer",
                reason="название не задано",
            )
        if stripped != self.name:
            object.__setattr__(self, "name", stripped)
        if self.spacing < 0:
            raise InvalidInput(
                subject="printer",
                reason=f"поля меньше 0, поля={self.spacing} мм",
            )
