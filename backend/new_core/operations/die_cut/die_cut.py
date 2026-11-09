"""One die cut of a press target."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DieCut:
    """
    Value Object. One die cut of a press target, priced from the operator salary.
    """

    operator_id: int
