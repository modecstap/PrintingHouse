"""A print run prices its operations, markup, and the order around them."""

import re
from decimal import Decimal

import pytest

from backend.core.accountant.money import Money
from backend.core.workplaces.lamination.models import Lamination
from backend.core.workplaces.printing.models import Chroma
from backend.new_core import (
    Accountant,
    Part,
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
    LaminationSpecification,
    AdditionalWork,
    Order,
    Paper,
    Percent,
    PressOperator,
    Print,
    PrintRun,
    Printer,
    Product,
    Sheet,
)


def build_worked_run(  # pylint: disable=too-many-arguments,too-many-locals
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
    markup: Percent = Percent(0),
) -> tuple[PrintRun, Print | None, Laminate | None, Cut | None]:
    """Assembles one run and the operations the flags allow. It does not price them.

    with_print, with_laminate, and with_cut default to True. A False flag
    skips that factory and returns None in its place. Chroma and
    lamination are stored on the block. die_cutting is false.

    The block sheet costs 999, the target sheet costs 9999, the order count
    is 4, and assembly costs 999. Those values stay out of the sheet report.
    The block count is 3 and scales only block_cost_report. Part markup
    defaults to 0. Two press sheets add a 30 percent volume markup.
    Paper thickness is 1 mm, so the 50 mm stack cuts both press sheets
    in one lift.
    """
    block = Part(
        sheet=Sheet(
            paper=Paper(
                density=60,
                thickness=1,
                name="block",
                price_per_kilo=Money(Decimal(999)),
            ),
            height=1,
            width=1,
        ),
        count=3,
        markup=markup,
        chroma=chroma,
        lamination=LaminationSpecification(
            lamination=lamination,
            film=Film(name="film", price=Money(Decimal(3)), density=77),
        ),
        die_cutting=False,
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
                    markup=Percent(0),
                ),
            ),
        ),
        count=4,
    )
    run = PrintRun(
        id=1,
        block=block,
        for_order=1,
        required_count=required_count,
        imposition=Imposition(
            target=Sheet(
                paper=Paper(
                    density=60,
                    thickness=1,
                    name="target",
                    price_per_kilo=Money(Decimal(9999)),
                ),
                height=target_height,
                width=target_width,
            ),
            press_sheet=Sheet(
                paper=Paper(
                    density=press_density,
                    thickness=1,
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
        run.print(
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
        run.laminate(
            laminator=Laminator(id=1, startup=Money(Decimal(10))),
            operator=LaminatorOperator(
                id=1,
                salary_by_operation=Money(Decimal(4)),
            ),
        )
        if with_laminate
        else None
    )
    cut = (
        run.cut(
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
    """Print, laminate, and cut price the press sheet at 13, 16, 44, and 21.9.

    Two press sheets add 30 percent of 73, so the sheet total is 94.9.
    Each target field is the press amount divided by 6. The block has 3
    sheets, so the block report is the target report times 3.
    """
    run, _, _, _ = build_worked_run()

    assert run.production_count() == 12
    assert run.press_sheet_count() == 2
    accountant = Accountant()
    sheet = accountant.sheet_cost_report(run)
    per_item = accountant.list_report(run)
    report = accountant.block_cost_report(run)

    assert sheet.material == Money(Decimal(13))
    assert sheet.startup == Money(Decimal(16))
    assert sheet.work == Money(Decimal(44))
    assert sheet.markup == Money(Decimal("21.9"))
    assert sheet.total() == Money(Decimal("94.9"))
    assert per_item.material == Money(Decimal(13) / Decimal(6))
    assert per_item.startup == Money(Decimal(16) / Decimal(6))
    assert per_item.work == Money(Decimal(44) / Decimal(6))
    assert per_item.markup == Money(Decimal("21.9") / Decimal(6))
    assert per_item.total() == Money(Decimal("94.9") / Decimal(6))
    assert (
        per_item.material + per_item.startup + per_item.work + per_item.markup
        == per_item.total()
    )
    assert report.material == Money(Decimal(13) / Decimal(6) * 3)
    assert report.startup == Money(Decimal(16) / Decimal(6) * 3)
    assert report.work == Money(Decimal(44) / Decimal(6) * 3)
    assert report.markup == Money(Decimal("21.9") / Decimal(6) * 3)
    assert report.total() == (
        report.material + report.startup + report.work + report.markup
    )


def test_cost_report_drops_ink_and_printer_salary_for_zero_chroma():
    """ZERO_ZERO keeps paper and printer startup, and drops ink and press salary.

    The press sheet is 9, 16, 39, and 19.2. The total is 83.2.
    """
    run, _, _, _ = build_worked_run(chroma=Chroma.ZERO_ZERO)

    sheet = Accountant.sheet_cost_report(run)

    assert sheet.material == Money(Decimal(9))
    assert sheet.startup == Money(Decimal(16))
    assert sheet.work == Money(Decimal(39))
    assert sheet.markup == Money(Decimal("19.2"))
    assert sheet.total() == Money(Decimal("83.2"))


def test_cost_report_omits_lamination_when_it_is_not_passed():
    """Print and cut, without calling the laminate factory, price the press sheet.

    The press sheet is 10, 11, 40, and 18.3.
    """
    run, _, _, _ = build_worked_run(with_laminate=False)

    sheet = Accountant.sheet_cost_report(run)

    assert sheet.material == Money(Decimal(10))
    assert sheet.startup == Money(Decimal(11))
    assert sheet.work == Money(Decimal(40))
    assert sheet.markup == Money(Decimal("18.3"))
    assert sheet.total() == Money(Decimal("79.3"))


def test_cost_report_adds_paper_and_ink_for_a_second_print():
    """Two FOUR_ZERO prints and nothing else price the press sheet at 20, 22, 10, and 15.6."""
    run, printing, _, _ = build_worked_run(with_laminate=False, with_cut=False)
    second = run.print(
        printer=printing.printer,
        operator=printing.operator,
    )

    assert run.operations == [printing, second]
    assert printing is not second
    sheet = Accountant.sheet_cost_report(run)

    assert sheet.material == Money(Decimal(20))
    assert sheet.startup == Money(Decimal(22))
    assert sheet.work == Money(Decimal(10))
    assert sheet.markup == Money(Decimal("15.6"))
    assert sheet.total() == Money(Decimal("67.6"))


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

    sheet = Accountant.sheet_cost_report(run)

    assert sheet.material == Money(Decimal(material))


def test_list_report_divides_by_the_imposition_count():
    """One press sheet is divided by the 6 targets on it, then times 3 block sheets.

    The press sheet is 10, 10, 5, and 7.5. The sheet total is 32.5.
    """
    run, _, _, _ = build_worked_run(
        required_count=3,
        printer_startup=10,
        with_laminate=False,
        with_cut=False,
    )

    accountant = Accountant()
    sheet = accountant.sheet_cost_report(run)
    per_item = accountant.list_report(run)
    report = accountant.block_cost_report(run)

    assert run.press_sheet_count() == 1
    assert run.imposition.count() == 6
    assert sheet.material == Money(Decimal(10))
    assert sheet.startup == Money(Decimal(10))
    assert sheet.work == Money(Decimal(5))
    assert sheet.markup == Money(Decimal("7.5"))
    assert sheet.total() == Money(Decimal("32.5"))
    assert per_item.material == Money(Decimal(10) / Decimal(6))
    assert per_item.startup == Money(Decimal(10) / Decimal(6))
    assert per_item.work == Money(Decimal(5) / Decimal(6))
    assert per_item.markup == Money(Decimal("7.5") / Decimal(6))
    assert per_item.total() == Money(Decimal("32.5") / Decimal(6))
    assert report.material == Money(Decimal(10) / Decimal(6) * 3)
    assert report.startup == Money(Decimal(10) / Decimal(6) * 3)
    assert report.work == Money(Decimal(5) / Decimal(6) * 3)
    assert report.markup == Money(Decimal("7.5") / Decimal(6) * 3)
    assert report.total() == Money(Decimal("32.5") / Decimal(6) * 3)


def test_cost_report_is_zero_without_operations():
    """No operations price every money field at zero and still produce 12 sheets."""
    run, _, _, _ = build_worked_run(
        with_print=False,
        with_laminate=False,
        with_cut=False,
    )

    assert not run.operations
    assert run.production_count() == 12
    report = Accountant().block_cost_report(run)

    assert report.material == Money.zero()
    assert report.startup == Money.zero()
    assert report.work == Money.zero()
    assert report.markup == Money.zero()
    assert report.total() == Money.zero()


def test_cost_report_is_zero_for_lamination_with_no_sides():
    """Lamination DONT leaves the press sheet at 10, 11, 40, and 18.3."""
    run, _, _, _ = build_worked_run(lamination=Lamination.DONT)

    sheet = Accountant.sheet_cost_report(run)

    assert sheet.material == Money(Decimal(10))
    assert sheet.startup == Money(Decimal(11))
    assert sheet.work == Money(Decimal(40))
    assert sheet.markup == Money(Decimal("18.3"))
    assert sheet.total() == Money(Decimal("79.3"))


def test_cost_report_prices_two_film_sides_once_for_salary():
    """Two film sides price material at 6, startup at 5, and salary once at 4."""
    run, _, _, _ = build_worked_run(
        lamination=Lamination.ONE_ONE,
        with_print=False,
        with_cut=False,
    )

    sheet = Accountant.sheet_cost_report(run)

    assert sheet.material == Money(Decimal(6))
    assert sheet.startup == Money(Decimal(5))
    assert sheet.work == Money(Decimal(4))
    assert sheet.markup == Money(Decimal("4.5"))
    assert sheet.total() == Money(Decimal("19.5"))


def test_cost_report_adds_the_die_cutter_salary_once():
    """A die cut adds only the salary 8, and the target work is 8 divided by 6."""
    run, _, _, _ = build_worked_run(
        with_print=False,
        with_laminate=False,
        with_cut=False,
    )
    run.die_cut(
        operator=DieCutterOperator(
            id=1,
            salary_by_operation=Money(Decimal(8)),
        ),
    )

    accountant = Accountant()
    sheet = accountant.sheet_cost_report(run)
    per_item = accountant.list_report(run)

    assert sheet.material == Money(Decimal(0))
    assert sheet.startup == Money(Decimal(0))
    assert sheet.work == Money(Decimal(8))
    assert sheet.markup == Money(Decimal("2.4"))
    assert sheet.total() == Money(Decimal("10.4"))
    assert per_item.work == Money(Decimal(8) / Decimal(6))


def test_factories_append_in_call_order():
    """Factories append print, laminate, cut, then die cut, in call order.

    Print keeps the block chroma and the press sheet. Laminate keeps the
    block lamination. Cut keeps the imposition and the press sheet count.
    The die cut keeps the operator that was passed.
    """
    run, printing, laminate, cut = build_worked_run()
    operator = DieCutterOperator(
        id=1,
        salary_by_operation=Money(Decimal(8)),
    )
    die_cut = run.die_cut(operator=operator)

    assert run.operations == [printing, laminate, cut, die_cut]
    assert printing.spec.chroma is run.block.chroma
    assert printing.spec.paper is run.imposition.press_sheet
    assert laminate.spec is run.block.lamination
    assert cut.imposition is run.imposition
    assert cut.sheet_count == run.press_sheet_count()
    assert die_cut.operator is operator


def test_constructor_print_stays_out_of_the_run():
    """A Print built by its constructor stays out of the run.

    One factory print prices the press sheet at 10, 11, 5, and 7.8.
    Each target field is that amount divided by 6, and the target total
    is the sum of the four target parts.
    """
    run, printing, _, _ = build_worked_run(with_laminate=False, with_cut=False)
    Print(
        spec=printing.spec,
        printer=printing.printer,
        operator=printing.operator,
    )

    assert run.operations == [printing]
    accountant = Accountant()
    sheet = accountant.sheet_cost_report(run)
    per_item = accountant.list_report(run)

    assert sheet.material == Money(Decimal(10))
    assert sheet.startup == Money(Decimal(11))
    assert sheet.work == Money(Decimal(5))
    assert sheet.markup == Money(Decimal("7.8"))
    assert sheet.total() == Money(Decimal("33.8"))
    assert per_item.material == Money(Decimal(10) / Decimal(6))
    assert per_item.startup == Money(Decimal(11) / Decimal(6))
    assert per_item.work == Money(Decimal(5) / Decimal(6))
    assert per_item.markup == Money(Decimal("7.8") / Decimal(6))
    assert (
        per_item.total()
        == per_item.material + per_item.startup + per_item.work + per_item.markup
    )


def test_sheet_cost_report_adds_block_markup_to_volume_markup():
    """A 10 percent block markup and a 30 percent volume markup both use the base 73.

    The markups are 7.3 and 21.9. The second does not scale the first.
    """
    run, _, _, _ = build_worked_run(markup=Percent(10))

    sheet = Accountant.sheet_cost_report(run)

    assert sheet.markup == Money(Decimal("29.2"))
    assert sheet.total() == Money(Decimal("102.2"))


def test_sheet_cost_report_uses_the_15_percent_volume_band():
    """Five press sheets add 15 percent of the ink, not 30."""
    run, _, _, _ = build_worked_run(
        required_count=24,
        chroma=Chroma.FOUR_ZERO,
        press_price=0,
        printer_startup=0,
        press_salary=0,
        with_laminate=False,
        with_cut=False,
    )

    sheet = Accountant.sheet_cost_report(run)

    assert run.press_sheet_count() == 5
    assert sheet.material == Money(Decimal(4))
    assert sheet.markup == Money(Decimal("0.6"))
    assert sheet.total() == Money(Decimal("4.6"))


def test_order_report_scales_the_product_by_tax_and_the_order_count():
    """Work of 100 with 10 percent markup is 110, then times 100/93, then times 4.

    The run has no operations, so its block report is zero. Income equals
    the order price because material and startup stay zero.
    """
    run, _, _, _ = build_worked_run(
        with_print=False,
        with_laminate=False,
        with_cut=False,
    )
    order = Order(
        id=1,
        product=Product(
            blocks=(run.block,),
            operations=(
                AdditionalWork(
                    name="сборка",
                    price=Money(Decimal(100)),
                    description="склейка",
                    markup=Percent(10),
                ),
            ),
        ),
        count=4,
    )

    accountant = Accountant()
    priced = accountant.order_cost_report(
        [run],
        order.product.operations,
        order,
    )
    report = accountant.order_report(order, [run])

    compensation = Decimal(100) / Decimal(93)
    assert priced.work == Money(Decimal(400))
    assert priced.markup == Money(Decimal(40))
    assert priced.total() == Money(Decimal(440))
    assert report.product_price == (
        Money(Decimal(100) * compensation) + Money(Decimal(10) * compensation)
    )
    assert report.order_price == (
        Money(Decimal(400) * compensation) + Money(Decimal(40) * compensation)
    )
    assert report.income == report.order_price
    assert report.impositions == (6,)


def test_print_run_has_no_cost_report():
    """PrintRun has no cost_report."""
    assert not hasattr(PrintRun, "cost_report")


def test_print_run_rejects_a_required_count_of_zero():
    """A required count of 0 is rejected because the run prints no press sheets."""
    message = "print_run: печатных листов 0, необходимое количество=0"

    with pytest.raises(InvalidInput, match=f"^{re.escape(message)}$"):
        build_worked_run(required_count=0)
