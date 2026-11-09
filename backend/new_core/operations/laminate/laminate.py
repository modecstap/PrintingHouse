"""One lamination of a press target."""

from __future__ import annotations

from dataclasses import dataclass

from backend.new_core.materials.film import FilmID
from backend.new_core.operations.laminate.lamination import Lamination
from backend.new_core.equipment.laminator import LaminatorID
from backend.new_core.personal.laminator_operator import LaminatorOperatorID


@dataclass(frozen=True, slots=True)
class Laminate:
    """
    Value Object. One lamination of a press target: the specification,
    the laminator, and the operator.
    """

    laminator_id: LaminatorID
    operator_id: LaminatorOperatorID
    lamination: Lamination
    film_id: FilmID
