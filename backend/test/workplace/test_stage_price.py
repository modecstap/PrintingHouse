from decimal import Decimal

from backend.workplace.money import Money
from backend.workplace.pricing.cutting import price_cutting
from backend.workplace.pricing.die_cutting import price_die_cutting
from backend.workplace.pricing.lamination import price_lamination
from backend.workplace.pricing.printing import price_printing
from backend.workplace.pricing.stage_cost import StageCost
from backend.workplace.reports import (
    CuttingReport,
    DieCuttingReport,
    LaminationReport,
    PrintingReport,
)


def test_printing_price_charges_one_sheet_of_paper_and_ink_and_salary_once():
    report = PrintingReport(
        mass_kg=Decimal("2"),
        used_ink=(1, 0, 0, 0),
        sheet_count=3,
        human_operations=4,
    )
    result = price_printing(
        report,
        Decimal("10"),
        Decimal("8"),
        Decimal("3"),
        Decimal("9"),
    )
    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("20.66666666666666666666666667")),
        salary=Money(Decimal("9")),
    )


def test_printing_price_omits_salary_when_human_operations_are_zero():
    report = PrintingReport(
        mass_kg=Decimal("1"),
        used_ink=(0, 0, 0, 0),
        sheet_count=1,
        human_operations=0,
    )
    result = price_printing(
        report,
        Decimal("10"),
        Decimal("8"),
        Decimal("3"),
        Decimal("9"),
    )
    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("10")),
        salary=Money(Decimal("0")),
    )


def test_printing_price_omits_ink_when_sheet_count_is_zero():
    report = PrintingReport(
        mass_kg=Decimal("1"),
        used_ink=(5, 5, 5, 5),
        sheet_count=0,
        human_operations=2,
    )
    result = price_printing(
        report,
        Decimal("10"),
        Decimal("8"),
        Decimal("3"),
        Decimal("4"),
    )
    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("10")),
        salary=Money(Decimal("4")),
    )


def test_cutting_price_divides_cut_rate_by_internal_sheet_count():
    result = price_cutting(CuttingReport(human_cuts=1), Decimal("1"), 3)
    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("0")),
        salary=Money(Decimal("0.3333333333333333333333333333")),
    )


def test_cutting_price_divides_another_cut_rate():
    result = price_cutting(CuttingReport(human_cuts=3), Decimal("10"), 4)
    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("0")),
        salary=Money(Decimal("7.5")),
    )


def test_lamination_price_splits_film_and_does_not_round_startup():
    result = price_lamination(LaminationReport(film_sides=1), Decimal("1"), 3)
    assert result == StageCost(
        startup_cost=Money(Decimal("66.66666666666666666666666667")),
        material_cost=Money(Decimal("0.5")),
        salary=Money(Decimal("0.5")),
    )


def test_lamination_price_splits_another_film():
    result = price_lamination(LaminationReport(film_sides=2), Decimal("10"), 4)
    assert result == StageCost(
        startup_cost=Money(Decimal("50")),
        material_cost=Money(Decimal("10")),
        salary=Money(Decimal("10")),
    )


def test_die_cutting_price_uses_the_rate_once():
    result = price_die_cutting(DieCuttingReport(sheet_count=9), Decimal("15"))
    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("0")),
        salary=Money(Decimal("15")),
    )


def test_die_cutting_price_ignores_sheet_count():
    result = price_die_cutting(DieCuttingReport(sheet_count=100), Decimal("4"))
    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("0")),
        salary=Money(Decimal("4")),
    )
