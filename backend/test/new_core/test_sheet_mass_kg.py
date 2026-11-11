"""Sheet mass from paper density value object."""

from decimal import Decimal

from backend.new_core import Format, Paper, PaperDensity, PaperType, Sheet
from backend.new_core.materials.sheet import SheetID
from backend.new_core.values.money import Money


def test_sheet_mass_kg_uses_paper_density_value() -> None:
    """Mass matches width times height over area factor times density over 1000."""
    sheet = Sheet(
        id=SheetID(1),
        paper=Paper(
            density=PaperDensity(80),
            thickness=Decimal(1),
            type=PaperType("press"),
            price_per_kilo=Money(Decimal("1")),
        ),
        format=Format(name="fmt", height=1000, width=700),
    )
    expected = (
        Decimal(700)
        * Decimal(1000)
        / Decimal(1_000_000)
        * Decimal(80)
        / Decimal(1000)
    )
    assert sheet.mass_kg() == expected
