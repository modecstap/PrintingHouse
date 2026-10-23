from decimal import Decimal

import pytest

from backend.workplace.accountant.money import Money
from backend.workplace.accountant.pricing.cutting import CuttingCalculation
from backend.workplace.accountant.pricing.die_cutting import \
    DieCuttingCalculation
from backend.workplace.accountant.pricing.lamination import \
    LaminationCalculation
from backend.workplace.accountant.pricing.printing import \
    PrintingCalculation
from backend.workplace.accountant.pricing.stage_cost import StageCost
from backend.workplace.workplaces.cutting.models import CuttingReport
from backend.workplace.workplaces.die_cutting.models import DieCuttingReport
from backend.workplace.workplaces.lamination.models import LaminationReport
from backend.workplace.workplaces.printing.models import PrintingReport


def test_printing_price_charges_one_sheet_of_paper_and_ink_and_salary_once():
    report = PrintingReport(
        mass_kg=Decimal("2"),
        used_ink=(1, 0, 0, 0),
        sheet_count=3,
        human_operations=4,
    )
    result = PrintingCalculation(
        cyan=Money(Decimal("8") / 4),
        magenta=Money(Decimal("8") / 4),
        yellow=Money(Decimal("8") / 4),
        black=Money(Decimal("3")),
        paper=Money(Decimal("10")),
        salary=Money(Decimal("9")),
    ).attach(report).calculate()

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

    result = PrintingCalculation(
        cyan=Money(Decimal("8") / 4),
        magenta=Money(Decimal("8") / 4),
        yellow=Money(Decimal("8") / 4),
        black=Money(Decimal("3")),
        paper=Money(Decimal("10")),
        salary=Money(Decimal("9")),
    ).attach(report).calculate()

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

    result = PrintingCalculation(
        cyan=Money(Decimal("8") / 4),
        magenta=Money(Decimal("8") / 4),
        yellow=Money(Decimal("8") / 4),
        black=Money(Decimal("3")),
        paper=Money(Decimal("10")),
        salary=Money(Decimal("4")),
    ).attach(report).calculate()

    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("10")),
        salary=Money(Decimal("4")),
    )


def test_cutting_price_divides_cut_rate_by_internal_sheet_count():
    result = CuttingCalculation(salary=Money(Decimal("1"))).attach(
        CuttingReport(human_cuts=1), 3
    ).calculate()
    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("0")),
        salary=Money(Decimal("0.3333333333333333333333333333")),
    )


def test_cutting_price_divides_another_cut_rate():
    result = CuttingCalculation(salary=Money(Decimal("10"))).attach(
        CuttingReport(human_cuts=3), 4
    ).calculate()
    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("0")),
        salary=Money(Decimal("7.5")),
    )


def test_lamination_price_splits_film_and_does_not_round_startup():
    result = LaminationCalculation(
        startup=Money(Decimal("200")),
        film_cost=Money(Decimal("1") / 2),
        salary=Money((Decimal("1") / 2) * 1),
    ).attach(LaminationReport(film_sides=1), 3).calculate()
    assert result == StageCost(
        startup_cost=Money(Decimal("66.66666666666666666666666667")),
        material_cost=Money(Decimal("0.5")),
        salary=Money(Decimal("0.5")),
    )


def test_lamination_price_splits_another_film():
    result = LaminationCalculation(
        startup=Money(Decimal("200")),
        film_cost=Money(Decimal("10") / 2),
        salary=Money((Decimal("10") / 2) * 2),
    ).attach(LaminationReport(film_sides=2), 4).calculate()
    assert result == StageCost(
        startup_cost=Money(Decimal("50")),
        material_cost=Money(Decimal("10")),
        salary=Money(Decimal("10")),
    )


def test_die_cutting_price_uses_the_rate_once():
    result = DieCuttingCalculation(salary=Money(Decimal("15"))).attach(
        DieCuttingReport(sheet_count=9)
    ).calculate()
    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("0")),
        salary=Money(Decimal("15")),
    )


def test_die_cutting_price_ignores_sheet_count():
    result = DieCuttingCalculation(salary=Money(Decimal("4"))).attach(
        DieCuttingReport(sheet_count=100)
    ).calculate()
    assert result == StageCost(
        startup_cost=Money(Decimal("0")),
        material_cost=Money(Decimal("0")),
        salary=Money(Decimal("4")),
    )


def test_lamination_price_is_zero_when_film_sides_are_zero():
    result = LaminationCalculation(
        startup=Money(Decimal("200")),
        film_cost=Money(Decimal("5")),
        salary=Money(Decimal("10")),
    ).attach(LaminationReport(film_sides=0), 4).calculate()
    assert result == StageCost.zero()


def test_lamination_price_does_not_divide_when_film_sides_are_zero():
    result = LaminationCalculation(
        startup=Money(Decimal("200")),
        film_cost=Money(Decimal("5")),
        salary=Money(Decimal("10")),
    ).attach(LaminationReport(film_sides=0), 0).calculate()
    assert result == StageCost.zero()


def test_lamination_price_divides_startup_rate():
    result = LaminationCalculation(
        startup=Money(Decimal("100")),
        film_cost=Money(Decimal("1")),
        salary=Money(Decimal("2")),
    ).attach(LaminationReport(film_sides=1), 4).calculate()
    assert result == StageCost(
        startup_cost=Money(Decimal("25")),
        material_cost=Money(Decimal("1")),
        salary=Money(Decimal("2")),
    )


def test_die_cutting_price_is_zero_when_sheet_count_is_zero():
    result = DieCuttingCalculation(salary=Money(Decimal("15"))).attach(
        DieCuttingReport(sheet_count=0)
    ).calculate()
    assert result == StageCost.zero()


def test_cutting_price_rejects_second_attach():
    calculation = CuttingCalculation(salary=Money(Decimal("1")))
    calculation.attach(CuttingReport(human_cuts=1), 3)
    with pytest.raises(RuntimeError, match="^Report is already attached$"):
        calculation.attach(CuttingReport(human_cuts=1), 3)


def test_cutting_price_rejects_calculate_without_report():
    calculation = CuttingCalculation(salary=Money(Decimal("1")))
    with pytest.raises(RuntimeError, match="^Report is not attach$"):
        calculation.calculate()


def test_lamination_price_rejects_second_attach():
    calculation = LaminationCalculation(
        startup=Money(Decimal("1")),
        film_cost=Money(Decimal("1")),
        salary=Money(Decimal("1")),
    )
    calculation.attach(LaminationReport(film_sides=1), 3)
    with pytest.raises(RuntimeError, match="^Report is already attached$"):
        calculation.attach(LaminationReport(film_sides=1), 3)


def test_lamination_price_rejects_calculate_without_report():
    calculation = LaminationCalculation(
        startup=Money(Decimal("1")),
        film_cost=Money(Decimal("1")),
        salary=Money(Decimal("1")),
    )
    with pytest.raises(RuntimeError, match="^Report is not attach$"):
        calculation.calculate()


def test_die_cutting_price_rejects_second_attach():
    calculation = DieCuttingCalculation(salary=Money(Decimal("1")))
    calculation.attach(DieCuttingReport(sheet_count=1))
    with pytest.raises(RuntimeError, match="^Report is already attached$"):
        calculation.attach(DieCuttingReport(sheet_count=1))


def test_die_cutting_price_rejects_calculate_without_report():
    calculation = DieCuttingCalculation(salary=Money(Decimal("1")))
    with pytest.raises(RuntimeError, match="^Report is not attach$"):
        calculation.calculate()
