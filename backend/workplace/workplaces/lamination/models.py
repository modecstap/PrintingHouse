from dataclasses import dataclass


@dataclass(frozen=True)
class LaminationReport:
    film_sides: int

