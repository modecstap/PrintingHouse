"""One lamination of a press target."""

from __future__ import annotations

from dataclasses import dataclass

from backend.new_core.materials.film import Film
from backend.new_core.operations.laminate.lamination import Lamination


@dataclass(frozen=True, slots=True)
class Laminate:
    """
    Value Object. One lamination of a press target: the specification,
    the laminator, and the operator.
    """

    laminator_id: int
    operator_id: int
    lamination: Lamination
    film: Film
