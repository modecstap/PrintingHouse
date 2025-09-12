# --- Пример использования ---
from decimal import Decimal

from cost_reporter.cost_reporter_factory import CostReporterFactory
from cost_reporter.models.edition import Lamination, Chroma, Edition
from cost_reporter.models.list_size import ListSize
from cost_reporter.models.press_sheet import PressSheet
from cost_reporter.models.production import Production, CutterInfo

if __name__ == "__main__":
    production = Production(
        tax_rate=Decimal("0.93"),
        black_ink_cost=Decimal("1"),
        ink_cost=Decimal("15.6"),
        paper_cost=Decimal("165"),
        press_sheet=PressSheet(height=320, width=450, spacing=5),
        cutter=CutterInfo(stack_height=20),
        cutting_cost=Decimal("1.5"),
        die_cutting_cost=Decimal("100"),
        lamination_cost=Decimal("12"),
    )

    edition = Edition(
        count=200,
        list_size=ListSize(height=105, width=148, bleeds=2),
        density=300,
        chroma=Chroma.FOUR_ZERO,
        lamination=Lamination.DONT,
        die_cutting=False,
        markup=Decimal("1.8"),
    )

    reporter = CostReporterFactory(edition, production).create_reporter()
    print(reporter.get_report())