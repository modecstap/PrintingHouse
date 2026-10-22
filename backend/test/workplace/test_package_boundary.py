from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[2]
WORKPLACE = BACKEND / "workplace"

FORBIDDEN_NAMES = (
    "OrderFactoryService",
    "CostReporterFactory",
    "PrintingCostReporter",
    "OrderCostReporter",
    "SheetCostBuilder",
    "SheetCalculator",
    "EditionCalculator",
    "ItemCalculator",
    "TaxCalculator",
    "PaperStage",
    "PrintStage",
    "CutStage",
    "LaminationStage",
    "DieCuttingStage",
    "MarkupStage",
    "VolumeMarkupStage",
    "TaxCompensationStage",
    "consumed_sheets",
    "PrinterService",
    "backend.aggregate.printer.money",
    "backend.aggregate.printer.printer",
    "backend.aggregate.printer.service",
    "backend.aggregate.printer.events",
    "backend.aggregate.printer.errors",
    "backend.models.chroma",
    "backend.models.lamination",
    "models.Chroma",
    "models.Lamination",
)

ALLOWED_AGGREGATE_MODULES = (
    "backend.aggregate.printer.values.chroma",
    "backend.aggregate.laminator.values.lamination",
)

AGGREGATE = "backend.aggregate"


def test_workplace_sources_exclude_live_cost_and_toner_names():
    assert (BACKEND / "cost_reporter").is_dir()

    violations = []
    if WORKPLACE.is_dir():
        for path in sorted(WORKPLACE.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            violations.extend(_forbidden_in(path.name, text))

    if violations:
        pytest.fail("\n".join(violations))


def _forbidden_in(filename: str, text: str) -> list[str]:
    found = [f"{filename} contains {name}" for name in FORBIDDEN_NAMES if name in text]
    start = 0
    while True:
        index = text.find(AGGREGATE, start)
        if index < 0:
            break
        tail = text[index:]
        if not any(tail.startswith(module) for module in ALLOWED_AGGREGATE_MODULES):
            found.append(f"{filename} contains {AGGREGATE}")
        start = index + len(AGGREGATE)
    return found
