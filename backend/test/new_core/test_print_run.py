import re
from decimal import Decimal

import pytest

from backend.core.accountant.money import Money
from backend.core.workplaces.lamination.models import Lamination
from backend.core.workplaces.printing.models import Chroma
from backend.new_core import (
    Accountant,
    Block,
    Cut,
    Cutter,
    CutterOperator,
    DieCutterOperator,
    Film,
    Imposition,
    InvalidInput,
    Laminate,
    Laminator,
    LaminatorOperator,
    AdditionalWork,
    Order,
    Paper,
    PressOperator,
    Print,
    PrintRun,
    Printer,
    Product,
    Sheet,
)


def build_worked_run(
    *,
    target_width: int = 100,
    target_height: int = 100,
    press_width: int = 200,
    press_height: int = 300,
    press_density: int = 100,
    press_price: int = 1000,
    required_count: int = 10,
    chroma: Chroma = Chroma.FOUR_ZERO,
    printer_startup: int = 22,
    press_salary: int = 5,
    lamination: Lamination = Lamination.ONE_ZERO,
    max_stack: int = 50,
    with_print: bool = True,
    with_laminate: bool = True,
    with_cut: bool = True,
) -> tuple[PrintRun, Print | None, Laminate | None, Cut | None]:
    """Assembles one run and the operations the flags allow. It does not price them.

    with_print, with_laminate, and with_cut default to True. A False flag
    skips that factory and returns None in its place.

    The block sheet costs 999, the target sheet costs 9999, the block count
    is 3, the order count is 4, and assembly costs 999. Those values stay
    out of the report.
    """
    block = Block(
        sheet=Sheet(
            paper=Paper(density=60, name="block", price_per_kilo=Money(Decimal(999))),
            height=1,
            width=1,
        ),
        count=3,
    )
    Order(
        id=1,
        product=Product(
            blocks=(block,),
            operations=(
                AdditionalWork(
                    name="сборка",
                    price=Money(Decimal(999)),
                    description="склейка",
                ),
            ),
        ),
        count=4,
    )
    run = PrintRun(
        id=1,
        block=block,
        required_count=required_count,
        imposition=Imposition(
            target=Sheet(
                paper=Paper(
                    density=60,
                    name="target",
                    price_per_kilo=Money(Decimal(9999)),
                ),
                height=target_height,
                width=target_width,
            ),
            press_sheet=Sheet(
                paper=Paper(
                    density=press_density,
                    name="press",
                    price_per_kilo=Money(Decimal(press_price)),
                ),
                height=press_height,
                width=press_width,
            ),
            bleeds=0,
            spacing=0,
        ),
    )
    printing = (
        run.add_print(
            chroma=chroma,
            printer=Printer(
                id=1,
                startup=Money(Decimal(printer_startup)),
                cyan=Money(Decimal(1)),
                magenta=Money(Decimal(1)),
                yellow=Money(Decimal(1)),
                black=Money(Decimal(1)),
            ),
            operator=PressOperator(
                id=1,
                salary_by_operation=Money(Decimal(press_salary)),
            ),
        )
        if with_print
        else None
    )
    laminate = (
        run.add_laminate(
            lamination=lamination,
            laminator=Laminator(id=1, startup=Money(Decimal(10))),
            film=Film(name="film", price=Money(Decimal(3)), density=77),
            operator=LaminatorOperator(
                id=1,
                salary_by_operation=Money(Decimal(4)),
            ),
        )
        if with_laminate
        else None
    )
    cut = (
        run.add_cut(
            cutter=Cutter(id=1, max_stack=max_stack),
            operator=CutterOperator(
                id=1,
                salary_by_operation=Money(Decimal(7)),
            ),
        )
        if with_cut
        else None
    )
    return run, printing, laminate, cut


def test_cost_report_prices_the_worked_run():
    """Print, laminate, and cut price the press sheet at 13, 16, 44, and 73.

    The run produces 12 target sheets. Each target field is that press
    amount divided by 6, and the three target parts sum to the target total.
    """
    run, _, _, _ = build_worked_run()

    assert run.production_count() == 12
    report = Accountant().run_cost_report(run)

    assert report.press_sheet_material == Money(Decimal(13))
    assert report.press_sheet_startup == Money(Decimal(16))
    assert report.press_sheet_work == Money(Decimal(44))
    assert report.press_sheet_total == Money(Decimal(73))
    assert report.target_material == Money(Decimal(13) / Decimal(6))
    assert report.target_startup == Money(Decimal(16) / Decimal(6))
    assert report.target_work == Money(Decimal(44) / Decimal(6))
    assert report.target_total == Money(Decimal(73) / Decimal(6))
    assert (
        report.target_material + report.target_startup + report.target_work
        == report.target_total
    )


def test_cost_report_drops_ink_and_printer_salary_for_zero_chroma():
    """ZERO_ZERO keeps paper and printer startup, and drops ink and press salary.

    The press sheet is 9, 16, 39, and 64.
    """
    run, _, _, _ = build_worked_run(chroma=Chroma.ZERO_ZERO)

    report = Accountant().run_cost_report(run)

    assert report.press_sheet_material == Money(Decimal(9))
    assert report.press_sheet_startup == Money(Decimal(16))
    assert report.press_sheet_work == Money(Decimal(39))
    assert report.press_sheet_total == Money(Decimal(64))


def test_cost_report_omits_lamination_when_it_is_not_passed():
    """Print and cut, without calling the laminate factory, price the press sheet at 10, 11, 40, and 61."""
    run, _, _, _ = build_worked_run(with_laminate=False)

    report = Accountant().run_cost_report(run)

    assert report.press_sheet_material == Money(Decimal(10))
    assert report.press_sheet_startup == Money(Decimal(11))
    assert report.press_sheet_work == Money(Decimal(40))
    assert report.press_sheet_total == Money(Decimal(61))


def test_cost_report_adds_paper_and_ink_for_a_second_print():
    """Two FOUR_ZERO prints and nothing else price the press sheet at 20, 22, 10, and 52."""
    run, printing, _, _ = build_worked_run(with_laminate=False, with_cut=False)
    second = run.add_print(
        chroma=printing.chroma,
        printer=printing.printer,
        operator=printing.operator,
    )

    assert run.operations() == (printing, second)
    assert printing is not second
    report = Accountant().run_cost_report(run)

    assert report.press_sheet_material == Money(Decimal(20))
    assert report.press_sheet_startup == Money(Decimal(22))
    assert report.press_sheet_work == Money(Decimal(10))
    assert report.press_sheet_total == Money(Decimal(52))


@pytest.mark.parametrize(
    ("chroma", "material"),
    [
        (Chroma.ZERO_ZERO, 0),
        (Chroma.ONE_ZERO, 1),
        (Chroma.ONE_ONE, 2),
        (Chroma.FOUR_ZERO, 4),
        (Chroma.FOUR_ONE, 5),
        (Chroma.FOUR_FOUR, 8),
    ],
)
def test_press_sheet_material_equals_the_chroma_shares(
    chroma: Chroma,
    material: int,
):
    """One print with free paper, startup, and salary prices only the ink shares."""
    run, _, _, _ = build_worked_run(
        chroma=chroma,
        press_price=0,
        printer_startup=0,
        press_salary=0,
        with_laminate=False,
        with_cut=False,
    )

    report = Accountant().run_cost_report(run)

    assert report.press_sheet_material == Money(Decimal(material))


def test_cost_report_divides_the_target_by_the_smaller_count():
    """Three required sheets divide the press price by 3, not by the 6 that fit.

    The press sheet is 10, 10, 5, and 25.
    """
    run, _, _, _ = build_worked_run(
        required_count=3,
        printer_startup=10,
        with_laminate=False,
        with_cut=False,
    )

    report = Accountant().run_cost_report(run)

    assert report.press_sheet_material == Money(Decimal(10))
    assert report.press_sheet_startup == Money(Decimal(10))
    assert report.press_sheet_work == Money(Decimal(5))
    assert report.press_sheet_total == Money(Decimal(25))
    assert report.target_material == Money(Decimal(10) / Decimal(3))
    assert report.target_startup == Money(Decimal(10) / Decimal(3))
    assert report.target_work == Money(Decimal(5) / Decimal(3))
    assert report.target_total == Money(Decimal(25) / Decimal(3))


def test_cost_report_is_zero_without_operations():
    """No operations price every money field at zero and still produce 12 sheets."""
    run, _, _, _ = build_worked_run(
        with_print=False,
        with_laminate=False,
        with_cut=False,
    )

    assert run.operations() == ()
    assert run.production_count() == 12
    report = Accountant().run_cost_report(run)

    assert report.target_material == Money.zero()
    assert report.target_startup == Money.zero()
    assert report.target_work == Money.zero()
    assert report.target_total == Money.zero()
    assert report.press_sheet_material == Money.zero()
    assert report.press_sheet_startup == Money.zero()
    assert report.press_sheet_work == Money.zero()
    assert report.press_sheet_total == Money.zero()


def test_cost_report_is_zero_for_lamination_with_no_sides():
    """Lamination DONT leaves the press sheet at 10, 11, 40, and 61."""
    run, _, _, _ = build_worked_run(lamination=Lamination.DONT)

    report = Accountant().run_cost_report(run)

    assert report.press_sheet_material == Money(Decimal(10))
    assert report.press_sheet_startup == Money(Decimal(11))
    assert report.press_sheet_work == Money(Decimal(40))
    assert report.press_sheet_total == Money(Decimal(61))


def test_cost_report_prices_two_film_sides_once_for_salary():
    """Two film sides price material at 6, startup at 5, and salary once at 4."""
    run, _, _, _ = build_worked_run(
        lamination=Lamination.ONE_ONE,
        with_print=False,
        with_cut=False,
    )

    report = Accountant().run_cost_report(run)

    assert report.press_sheet_material == Money(Decimal(6))
    assert report.press_sheet_startup == Money(Decimal(5))
    assert report.press_sheet_work == Money(Decimal(4))
    assert report.press_sheet_total == Money(Decimal(15))


def test_cost_report_adds_the_die_cutter_salary_once():
    """A die cut adds only the salary 8, and the target work is 8 divided by 6."""
    run, _, _, _ = build_worked_run(
        with_print=False,
        with_laminate=False,
        with_cut=False,
    )
    run.add_die_cut(
        operator=DieCutterOperator(
            id=1,
            salary_by_operation=Money(Decimal(8)),
        ),
    )

    report = Accountant().run_cost_report(run)

    assert report.press_sheet_material == Money(Decimal(0))
    assert report.press_sheet_startup == Money(Decimal(0))
    assert report.press_sheet_work == Money(Decimal(8))
    assert report.press_sheet_total == Money(Decimal(8))
    assert report.target_work == Money(Decimal(8) / Decimal(6))


def test_factories_append_in_call_order():
    """Factories append print, laminate, cut, then die cut, in call order.

    Print, laminate, and cut point back at the run. The die cut has no
    print_run and keeps the operator that was passed.
    """
    run, printing, laminate, cut = build_worked_run()
    operator = DieCutterOperator(
        id=1,
        salary_by_operation=Money(Decimal(8)),
    )
    die_cut = run.add_die_cut(operator=operator)

    assert run.operations() == (printing, laminate, cut, die_cut)
    assert printing.print_run is run
    assert laminate.print_run is run
    assert cut.print_run is run
    assert not hasattr(die_cut, "print_run")
    assert die_cut.operator is operator


def test_constructor_print_stays_out_of_the_run():
    """A Print built by its constructor stays out of the run.

    One factory print prices the press sheet at 10, 11, 5, and 26.
    Each target field is that amount divided by 6, and the target total
    is the sum of the three target parts.
    """
    run, printing, _, _ = build_worked_run(with_laminate=False, with_cut=False)
    Print(
        chroma=printing.chroma,
        printer=printing.printer,
        operator=printing.operator,
        print_run=run,
    )

    assert run.operations() == (printing,)
    report = Accountant().run_cost_report(run)

    assert report.press_sheet_material == Money(Decimal(10))
    assert report.press_sheet_startup == Money(Decimal(11))
    assert report.press_sheet_work == Money(Decimal(5))
    assert report.press_sheet_total == Money(Decimal(26))
    assert report.target_material == Money(Decimal(10) / Decimal(6))
    assert report.target_startup == Money(Decimal(11) / Decimal(6))
    assert report.target_work == Money(Decimal(5) / Decimal(6))
    assert report.target_total == (
        report.target_material + report.target_startup + report.target_work
    )


def test_print_run_has_no_cost_report():
    """PrintRun has no cost_report."""
    assert not hasattr(PrintRun, "cost_report")


def test_print_run_rejects_a_required_count_of_zero():
    """A required count of 0 is rejected because the run prints no press sheets."""
    message = "print_run: печатных листов 0, необходимое количество=0"

    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        build_worked_run(required_count=0)
