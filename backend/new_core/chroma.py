"""Print color mode: catalog row with CMYK fill percents."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from backend.new_core.errors import InvalidInput
from backend.new_core.values.percent import Percent


__all__ = [
    "ChromaID",
    "Chroma",
]


@dataclass(frozen=True, slots=True)
class ChromaID:
    """Value Object. Stable identifier of a chroma row in the catalog."""

    value: int

    def __post_init__(self) -> None:
        """Rejects negative ids.

        :raises InvalidInput: when ``value`` is below zero.
        """
        if self.value < 0:
            raise InvalidInput(
                "chroma id",
                f"id меньше 0, id={self.value}",
            )


@dataclass(frozen=True, slots=True)
class Chroma:
    """Entity. One chroma catalog row: name and CMYK fill percents."""

    id: ChromaID
    name: str
    cyan: Percent
    magenta: Percent
    yellow: Percent
    black: Percent

    def __post_init__(self) -> None:
        """Rejects negative fill percents.

        :raises InvalidInput: if any CMYK fill is below zero. All failures
        are reported together.
        """
        reasons: list[str] = []
        if self.cyan.value < 0:
            reasons.append(f"C меньше 0, C={self.cyan.value}%")
        if self.magenta.value < 0:
            reasons.append(f"M меньше 0, M={self.magenta.value}%")
        if self.yellow.value < 0:
            reasons.append(f"Y меньше 0, Y={self.yellow.value}%")
        if self.black.value < 0:
            reasons.append(f"K меньше 0, K={self.black.value}%")
        if reasons:
            raise InvalidInput(
                subject="Chroma",
                reason=reasons,
            )

    def consumed_sheets(self) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        """Returns cyan, magenta, yellow, and black ink shares per press sheet.

        :return: each channel as ``Percent.value / 100``.
        """
        return (
            Decimal(self.cyan.value) / Decimal(100),
            Decimal(self.magenta.value) / Decimal(100),
            Decimal(self.yellow.value) / Decimal(100),
            Decimal(self.black.value) / Decimal(100),
        )