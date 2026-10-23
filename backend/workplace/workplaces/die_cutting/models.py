from dataclasses import dataclass


@dataclass(frozen=True)
class DieCuttingReport:
    sheet_count: int