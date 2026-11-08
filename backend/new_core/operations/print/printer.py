"""A printer: its startup and the price of each ink."""

from dataclasses import dataclass

from backend.core.accountant.money import Money


@dataclass(frozen=True)
class Printer:
    """A printer: its startup and the price of each ink."""

    id: int
    startup: Money
    cyan: Money
    magenta: Money
    yellow: Money
    black: Money
