from dataclasses import dataclass


@dataclass(frozen=True)
class CuttingReport:
    human_cuts: int
