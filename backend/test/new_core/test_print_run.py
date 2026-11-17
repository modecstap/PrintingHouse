"""Shared fixtures and builders for print-run pricing tests."""

from dataclasses import dataclass, field, replace
from decimal import Decimal

from backend.new_core.accountant.pricing.factory import PricingStrategyFactory
from backend.new_core.accountant.run_estimate import RunEstimate
from backend.new_core.application_services.order import OrderService
from backend.new_core.order.factory import OrderFactory
from backend.new_core.print_run.factory import PrintRunFactory
from backend.test.new_core.in_memory_repositories import InMemoryUnitOfWork
from backend.test.new_core.in_memory_repositories import (
    InMemoryCutterOperatorRepository,
    InMemoryCutterRepository,
    InMemoryDieCutterOperatorRepository,
    InMemoryFilmRepository,
    InMemoryLaminatorOperatorRepository,
    InMemoryLaminatorRepository,
    InMemoryPressOperatorRepository,
    InMemoryPrinterRepository,
)
from backend.new_core.equipment.cutter import Cutter, CutterID
from backend.new_core.equipment.laminator import Laminator, LaminatorID
from backend.new_core.equipment.printer import Printer, PrinterID, PrinterPrices
from backend.new_core.materials.film import Film, FilmID
from backend.new_core.materials.film_density import FilmDensity
from backend.new_core.materials.sheet import Sheet, SheetID
from backend.new_core.order.order import Order, OrderID
from backend.new_core.personal.cutter_operator import (
    CutterOperator,
    CutterOperatorID,
)
from backend.new_core.personal.die_cutter_operator import (
    DieCutterOperator,
    DieCutterOperatorID,
)
from backend.new_core.personal.laminator_operator import (
    LaminatorOperator,
    LaminatorOperatorID,
)
from backend.new_core.personal.press_operator import (
    PressOperator,
    PressOperatorID,
)
from backend.new_core.print_run.print_run import PrintRun, PrintRunID
from backend.new_core.values.money import Money
from backend.new_core.operations.laminate.lamination import Lamination
from backend.new_core.operations.print.chroma import Chroma
from backend.new_core.edges import Edges, EdgesID
from backend.new_core import (
    Cut,
    Format,
    Imposition,
    Laminate,
    Part,
    Paper,
    PaperDensity,
    PaperType,
    Percent,
    Print,
    Product,
)
from backend.new_core.operations.die_cut.die_cut import DieCut
from backend.test.storage.helpers import (
    TEST_ORDER_CREATED_AT,
    assembly_additional_work,
)


__all__ = [
    "pricing_strategy_factory",
    "order_service",
    "build_worked_run",
    "build_run_without_block_operations",
    "assert_tax_scaling_report_prices",
    "build_run_with_free_chroma_pricing",
    "tax_scaling_order",
    "attach_die_cut_operator",
]

@dataclass
class _RunPricingFixtures:  # pylint: disable=too-many-instance-attributes
    """Equipment and staff looked up by id when building test run estimates.

    Nine independent in-memory catalogs; nesting them would only rename access.
    """
    printers: dict[PrinterID, Printer] = field(default_factory=dict)
    press_operators: dict[PressOperatorID, PressOperator] = field(
        default_factory=dict,
    )
    laminators: dict[LaminatorID, Laminator] = field(default_factory=dict)
    laminator_operators: dict[LaminatorOperatorID, LaminatorOperator] = field(
        default_factory=dict,
    )
    cutter_operators: dict[CutterOperatorID, CutterOperator] = field(
        default_factory=dict,
    )
    die_cut_operators: dict[DieCutterOperatorID, DieCutterOperator] = field(
        default_factory=dict,
    )
    cutters: dict[CutterID, Cutter] = field(default_factory=dict)
    sheets: dict[SheetID, Sheet] = field(default_factory=dict)
    films: dict[FilmID, Film] = field(default_factory=dict)


@dataclass
class _WorkedRunCatalog:
    """Catalog rows used when assembling a worked run."""

    printer: Printer
    press_operator: PressOperator
    laminator: Laminator
    laminator_operator: LaminatorOperator
    cutter: Cutter
    cutter_operator: CutterOperator
    press_sheet: Sheet
    film: Film
    resolved_film_id: FilmID


def pricing_strategy_factory(
    ctx: _RunPricingFixtures,
    *,
    printers: InMemoryPrinterRepository | None = None,
    films: InMemoryFilmRepository | None = None,
) -> PricingStrategyFactory:
    """In-memory catalogs for pricing strategy tests.

    :param ctx: shared test fixtures.
    :param printers: the printers.
    :param films: the films.

    :return: the PricingStrategyFactory result.
    """
    printer_repo = printers or InMemoryPrinterRepository(
        items=dict(ctx.printers))
    film_repo = films or InMemoryFilmRepository(items=dict(ctx.films))
    return PricingStrategyFactory(
        printer_repo,
        InMemoryPressOperatorRepository(items=dict(ctx.press_operators)),
        InMemoryLaminatorRepository(items=dict(ctx.laminators)),
        InMemoryLaminatorOperatorRepository(
            items=dict(ctx.laminator_operators)),
        InMemoryCutterRepository(items=dict(ctx.cutters)),
        InMemoryCutterOperatorRepository(items=dict(ctx.cutter_operators)),
        InMemoryDieCutterOperatorRepository(items=dict(ctx.die_cut_operators)),
        film_repo,
    )


def order_service(
    uow: InMemoryUnitOfWork,
    ctx: _RunPricingFixtures,
    *,
    films: InMemoryFilmRepository | None = None,
) -> OrderService:
    """OrderService wired like production with in-memory catalogs.

    :param uow: the uow.
    :param ctx: shared test fixtures.
    :param films: the films.

    :return: the OrderService result.
    """
    pricing_factory = pricing_strategy_factory(ctx, films=films)
    return OrderService(
        uow=uow,
        order_factory=OrderFactory(uow.orders),
        print_run_factory=PrintRunFactory(uow.print_runs),
        pricing_factory=pricing_factory,
    )


def _worked_run_catalog(  # pylint: disable=too-many-arguments
    *,
    printer_startup: int,
    press_salary: int,
    max_stack: int,
    paper_thickness: Decimal,
    press_density: int,
    press_price: int,
    press_width: int,
    press_height: int,
    sheet_id: SheetID | None,
    film_id: FilmID | None,
) -> _WorkedRunCatalog:
    """Builds default catalog entities for :func:`build_worked_run`.

    :param printer_startup: the printer startup.
    :param press_salary: the press salary.
    :param max_stack: the max stack.
    :param paper_thickness: the paper thickness.
    :param press_density: the press density.
    :param press_price: the press price.
    :param press_width: the press width.
    :param press_height: the press height.
    :param sheet_id: id of the sheet.
    :param film_id: id of the film.

    :return: the _WorkedRunCatalog result.
    """
    printer = Printer(
        id=PrinterID(1),
        name="№ 1",
        spacing=0,
        prices=PrinterPrices(
            startup=Money(Decimal(printer_startup)),
            cyan=Money(Decimal(1)),
            magenta=Money(Decimal(1)),
            yellow=Money(Decimal(1)),
            black=Money(Decimal(1)),
        ),
    )
    press_operator = PressOperator(
        id=PressOperatorID(1),
        name="№ 1",
        salary_by_operation=Money(Decimal(press_salary)),
    )
    laminator = Laminator(
        id=LaminatorID(1),
        name="№ 1",
        startup=Money(Decimal(10)),
    )
    laminator_operator = LaminatorOperator(
        id=LaminatorOperatorID(1),
        name="№ 1",
        salary_by_operation=Money(Decimal(4)),
    )
    resolved_sheet_id = sheet_id or SheetID(1)
    resolved_film_id = film_id or FilmID(1)
    film = Film(
        id=resolved_film_id,
        name="film",
        price=Money(Decimal(3)),
        density=FilmDensity(77),
    )
    cutter = Cutter(id=CutterID(1), name="№ 1", max_stack=max_stack)
    cutter_operator = CutterOperator(
        id=CutterOperatorID(1),
        name="№ 1",
        salary_by_operation=Money(Decimal(7)),
    )
    press_sheet = Sheet(
        id=resolved_sheet_id,
        paper=Paper(
            density=PaperDensity(press_density),
            thickness=paper_thickness,
            type=PaperType("press"),
            price_per_kilo=Money(Decimal(press_price)),
        ),
        format=Format(
            name="press",
            height=press_height,
            width=press_width,
        ),
    )
    return _WorkedRunCatalog(
        printer=printer,
        press_operator=press_operator,
        laminator=laminator,
        laminator_operator=laminator_operator,
        cutter=cutter,
        cutter_operator=cutter_operator,
        press_sheet=press_sheet,
        film=film,
        resolved_film_id=resolved_film_id,
    )


def _worked_run_block_operations(
    catalog: _WorkedRunCatalog,
    *,
    with_print: bool,
    with_laminate: bool,
    with_cut: bool,
    chroma: Chroma,
    lamination: Lamination,
) -> tuple[tuple[object, ...], Print | None, Laminate | None, Cut | None]:
    """Builds block operations for :func:`build_worked_run`.

    :param catalog: the catalog.
    :param with_print: the with print.
    :param with_laminate: the with laminate.
    :param with_cut: the with cut.
    :param chroma: the chroma.
    :param lamination: the lamination.

    :return: the tuple[tuple[object, ...], Print | None, Laminate | None, Cut | None] result.
    """
    run_operations: list = []
    printing = None
    if with_print:
        printing = Print(
            printer_id=catalog.printer.id,
            operator_id=catalog.press_operator.id,
            chroma=chroma,
        )
        run_operations.append(printing)
    laminate = None
    if with_laminate:
        laminate = Laminate(
            laminator_id=catalog.laminator.id,
            operator_id=catalog.laminator_operator.id,
            lamination=lamination,
            film_id=catalog.resolved_film_id,
        )
        run_operations.append(laminate)
    cut = None
    if with_cut:
        cut = Cut(
            cutter_id=catalog.cutter.id,
            operator_id=catalog.cutter_operator.id,
        )
        run_operations.append(cut)
    return tuple(run_operations), printing, laminate, cut


def build_worked_run(  # pylint: disable=too-many-arguments
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
    paper_thickness: Decimal = Decimal(1),
    with_print: bool = True,
    with_laminate: bool = True,
    with_cut: bool = True,
    parts_markup: Percent = Percent(0),
    sheet_id: SheetID | None = None,
    film_id: FilmID | None = None,
) -> tuple[
    PrintRun,
    Print | None,
    Laminate | None,
    Cut | None,
    _RunPricingFixtures,
]:
    """Assembles one run and the operations the flags allow.

    :param target_width: the target width.
    :param target_height: the target height.
    :param press_width: the press width.
    :param press_height: the press height.
    :param press_density: the press density.
    :param press_price: the press price.
    :param required_count: the required count.
    :param chroma: the chroma.
    :param printer_startup: the printer startup.
    :param press_salary: the press salary.
    :param lamination: the lamination.
    :param max_stack: the max stack.
    :param paper_thickness: the paper thickness.
    :param with_print: the with print.
    :param with_laminate: the with laminate.
    :param with_cut: the with cut.
    :param parts_markup: the parts markup.
    :param sheet_id: id of the sheet.
    :param film_id: id of the film.

    :return: the tuple[PrintRun, Print | None, Laminate | None, Cut | None, _RunPricingFixtures] result.
    """
    catalog = _worked_run_catalog(
        printer_startup=printer_startup,
        press_salary=press_salary,
        max_stack=max_stack,
        paper_thickness=paper_thickness,
        press_density=press_density,
        press_price=press_price,
        press_width=press_width,
        press_height=press_height,
        sheet_id=sheet_id,
        film_id=film_id,
    )
    imposition = Imposition(
        target=Format(
            name="target",
            height=target_height,
            width=target_width,
        ),
        press_sheet=catalog.press_sheet,
        edges=Edges(id=EdgesID(1), name="", bleeds=0, spacing=0),
    )
    run_operations, printing, laminate, cut = _worked_run_block_operations(
        catalog,
        with_print=with_print,
        with_laminate=with_laminate,
        with_cut=with_cut,
        chroma=chroma,
        lamination=lamination,
    )
    block = Part(
        imposition=imposition,
        count=3,
        need_spacing=True,
        operations=run_operations,
    )
    Order(
        id=OrderID(1),
        product=Product(
            parts_markup=parts_markup,
            blocks=(block,),
            operations=(assembly_additional_work(),),
        ),
        count=4,
        description="",
        created_at=TEST_ORDER_CREATED_AT,
    )
    run = PrintRun(
        id=PrintRunID(1),
        block=block,
        for_order=OrderID(1),
        required_count=required_count,
    )
    sheet = catalog.press_sheet
    ctx = _RunPricingFixtures(
        printers={catalog.printer.id: catalog.printer},
        press_operators={catalog.press_operator.id: catalog.press_operator},
        laminators={catalog.laminator.id: catalog.laminator},
        laminator_operators={
            catalog.laminator_operator.id: catalog.laminator_operator,
        },
        cutter_operators={catalog.cutter_operator.id: catalog.cutter_operator},
        cutters={catalog.cutter.id: catalog.cutter},
        sheets={sheet.id: sheet},
        films={catalog.film.id: catalog.film},
    )
    return run, printing, laminate, cut, ctx


def build_run_without_block_operations(
    **kwargs,
) -> tuple[
    PrintRun,
    Print | None,
    Laminate | None,
    Cut | None,
    _RunPricingFixtures,
]:
    """Worked run whose block has no print, laminate, or cut operations.

    :param kwargs: the kwargs.

    :return: the tuple[PrintRun, Print | None, Laminate | None, Cut | None, _RunPricingFixtures] result.
    """
    return build_worked_run(
        with_print=False,
        with_laminate=False,
        with_cut=False,
        **kwargs,
    )


def assert_tax_scaling_report_prices(report: object) -> None:
    """Shared asserts for tax and order-count scaling on order reports.

    :param report: the report.
    """
    compensation = Decimal(100) / Decimal(93)
    assert report.product_price == (
        Money(Decimal(100) * compensation) + Money(Decimal(10) * compensation)
    )
    assert report.order_price == (
        Money(Decimal(400) * compensation) + Money(Decimal(40) * compensation)
    )
    assert report.income == report.order_price
    assert report.impositions == (6,)


def build_run_with_free_chroma_pricing(*,
                                       chroma: Chroma | None = None,
                                       required_count: int | None = None,
                                       ) -> tuple[PrintRun,
                                                  Print | None,
                                                  Laminate | None,
                                                  Cut | None,
                                                  _RunPricingFixtures]:
    """Worked run with zero paper, startup, and press salary.

    :param chroma: the chroma.
    :param required_count: the required count.

    :return: the tuple[PrintRun, Print | None, Laminate | None, Cut | None, _RunPricingFixtures] result.
    """
    kwargs: dict = {
        "press_price": 0,
        "printer_startup": 0,
        "press_salary": 0,
        "with_laminate": False,
        "with_cut": False,
    }
    if chroma is not None:
        kwargs["chroma"] = chroma
    if required_count is not None:
        kwargs["required_count"] = required_count
    return build_worked_run(**kwargs)


def tax_scaling_order(run: PrintRun) -> Order:
    """Order with сборка work priced for tax and count scaling tests.

    :param run: the run.

    :return: the Order result.
    """
    return Order(
        id=OrderID(1),
        product=Product(
            parts_markup=Percent(0),
            blocks=(run.block,),
            operations=(
                assembly_additional_work(
                    price=Decimal(100),
                    markup=Percent(10),
                ),
            ),
        ),
        count=4,
        description="",
        created_at=TEST_ORDER_CREATED_AT,
    )


def attach_die_cut_operator(
    run: PrintRun,
    ctx: _RunPricingFixtures,
    *,
    operator_id: int = 2,
    salary: Decimal = Decimal(8),
) -> DieCutterOperator:
    """Appends a die-cut operation and registers the operator on ``ctx``.

    :param run: the run.
    :param ctx: shared test fixtures.
    :param operator_id: id of the operator.
    :param salary: the salary.

    :return: the DieCutterOperator result.
    """
    die_operator = DieCutterOperator(
        id=DieCutterOperatorID(operator_id),
        name=f"№ {operator_id}",
        salary_by_operation=Money(salary),
    )
    _append_block_operation(run, DieCut(operator_id=die_operator.id))
    ctx.die_cut_operators[die_operator.id] = die_operator
    return die_operator


def _append_block_operation(run: PrintRun, operation: object) -> None:
    """Handles append block operation.

    :param run: the run.
    :param operation: the operation.
    """
    run.block = replace(
        run.block, operations=run.block.operations + (operation,))


def _estimate(
    run: PrintRun,
    ctx: _RunPricingFixtures,
    *,
    parts_markup: Percent = Percent(0),
) -> RunEstimate:
    """Handles estimate.

    :param run: the run.
    :param ctx: shared test fixtures.
    :param parts_markup: the parts markup.

    :return: the RunEstimate result.
    """
    strategies = [
        pricing_strategy_factory(ctx).create(operation, run)
        for operation in run.block.operations
    ]
    return RunEstimate.create(strategies, run=run, parts_markup=parts_markup)
