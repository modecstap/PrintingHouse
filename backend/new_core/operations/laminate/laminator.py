"""A laminator and its startup price."""

from dataclasses import dataclass

from backend.new_core.accountant.money import Money


@dataclass(frozen=True)
class Laminator:
    """A laminator and its startup price."""

    id: int
    startup: Money
