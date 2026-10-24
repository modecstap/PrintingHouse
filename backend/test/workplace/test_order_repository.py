import re
from collections.abc import Iterator
from dataclasses import fields
from decimal import Decimal

import pytest
from sqlalchemy import bindparam, text
from sqlalchemy.engine import Engine

from backend.workplace.accountant.money import Money
from backend.workplace.accountant.pricing.cutting import CuttingCalculation
from backend.workplace.accountant.pricing.die_cutting import (
    DieCuttingCalculation,
)
from backend.workplace.accountant.pricing.lamination import (
    LaminationCalculation,
)
from backend.workplace.accountant.pricing.printing import PrintingCalculation
from backend.workplace.cost_order import List, Order, Printing, Status
from backend.workplace.order_repository import OrderNotFound
from backend.workplace.reports import CostReport, PrintingCost
from backend.workplace.workplaces.lamination.models import Lamination
from backend.workplace.workplaces.printing.models import Chroma, PressSheet
from backend.workplace_order_db import (
    SqlWorkplaceOrderRepository,
    create_sync_engine,
)

_MISSING_ID = 9_000_000_000_001


def _money(amount: Decimal) -> Money:
    return Money(amount)


def _printing(
    count: int,
    chroma: Chroma,
    lamination: Lamination,
    die_cutting: bool,
    sheet_by_fitting: int,
    stack_height: int,
    press_sheet: PressSheet,
    sheet: List,
    press: tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal],
    cut: Decimal,
    lamination_rates: tuple[Decimal, Decimal, Decimal],
    die_cut: Decimal,
) -> Printing:
    startup, film_cost, salary = lamination_rates
    return Printing(
        count=count,
        chroma=chroma,
        lamination=lamination,
        die_cutting=die_cutting,
        sheet_by_fitting=sheet_by_fitting,
        stack_height=stack_height,
        press_sheet=press_sheet,
        list=sheet,
        press_pricing=PrintingCalculation(
            _money(press[0]),
            _money(press[1]),
            _money(press[2]),
            _money(press[3]),
            _money(press[4]),
            _money(press[5]),
        ),
        cut_pricing=CuttingCalculation(_money(cut)),
        lamination_pricing=LaminationCalculation(
            _money(startup),
            _money(film_cost),
            _money(salary),
        ),
        die_cut_pricing=DieCuttingCalculation(_money(die_cut)),
    )


def _full_order() -> Order:
    zero = Decimal(0)
    first = _printing(
        3,
        Chroma.FOUR_FOUR,
        Lamination.ONE_ONE,
        True,
        2,
        50,
        PressSheet(150, 320, 450, 2),
        List(90, 50, 2),
        (
            Decimal("1.10"),
            Decimal("2.20"),
            Decimal("3.30"),
            Decimal("4.40"),
            Decimal("5.50"),
            Decimal("6.60"),
        ),
        Decimal("7.70"),
        (Decimal("200"), Decimal("8.80"), Decimal("9.90")),
        Decimal("10.10"),
    )
    second = _printing(
        1,
        Chroma.ZERO_ZERO,
        Lamination.DONT,
        False,
        0,
        1,
        PressSheet(80, 100, 100, 0),
        List(10, 20, 0),
        (zero, zero, zero, zero, zero, zero),
        zero,
        (zero, zero, zero),
        zero,
    )
    return Order(
        unit_count=12,
        tax_rate=Decimal("0.93"),
        markup=Decimal("20"),
        operation_costs=(Decimal("10.5"), Decimal("-1.25")),
        printings=(first, second),
        comment="а" * 501,
        status=Status.IN_WORK,
    )


def _bare_order(order_id: int | None = None) -> Order:
    return Order(
        unit_count=1,
        tax_rate=Decimal("0"),
        markup=Decimal("0"),
        operation_costs=(),
        printings=(),
        id=order_id,
    )


def _report_a() -> CostReport:
    return CostReport(
        unit_cost_price=Decimal("1.5"),
        unit_cost=Decimal("2.5"),
        edition_cost=Decimal("3.5"),
        profit_after_tax=Decimal("-4.5"),
        printing_cost_reports=(
            PrintingCost(
                items_per_sheet=4,
                sheet_count=5,
                unit_cost_price=Decimal("1"),
                unit_cost=Decimal("2"),
                edition_cost_price=Decimal("3"),
                edition_cost=Decimal("4"),
                profit_before_tax=Decimal("-5"),
                profit_after_tax=Decimal("-6"),
            ),
        ),
    )


def _report_b() -> CostReport:
    return CostReport(
        unit_cost_price=Decimal("8"),
        unit_cost=Decimal("9"),
        edition_cost=Decimal("10"),
        profit_after_tax=Decimal("11"),
        printing_cost_reports=(),
    )


def _save(
    store: SqlWorkplaceOrderRepository,
    saved_ids: list[int],
    order: Order,
) -> int:
    order_id = store.save(order)
    saved_ids.append(order_id)
    return order_id


def _count_rows(engine: Engine, table: str) -> int:
    with engine.connect() as connection:
        count = connection.execute(
            text(f"SELECT count(*) FROM {table}")
        ).scalar_one()
    return int(count)


def _public_table_names(engine: Engine) -> set[str]:
    query = text(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public'"
    )
    with engine.connect() as connection:
        return set(connection.execute(query).scalars().all())


def _assert_printing(taken: Printing, original: Printing) -> None:
    assert taken.count == original.count
    assert taken.chroma is original.chroma
    assert taken.lamination is original.lamination
    assert taken.die_cutting is original.die_cutting
    assert taken.sheet_by_fitting == original.sheet_by_fitting
    assert taken.stack_height == original.stack_height
    assert taken.press_sheet == original.press_sheet
    assert taken.list == original.list
    assert taken.press_pricing.cyan == original.press_pricing.cyan
    assert taken.press_pricing.magenta == original.press_pricing.magenta
    assert taken.press_pricing.yellow == original.press_pricing.yellow
    assert taken.press_pricing.black == original.press_pricing.black
    assert taken.press_pricing.paper == original.press_pricing.paper
    assert taken.press_pricing.salary == original.press_pricing.salary
    assert taken.cut_pricing.salary == original.cut_pricing.salary
    startup = taken.lamination_pricing.startup
    assert startup == original.lamination_pricing.startup
    film_cost = taken.lamination_pricing.film_cost
    assert film_cost == original.lamination_pricing.film_cost
    salary = taken.lamination_pricing.salary
    assert salary == original.lamination_pricing.salary
    assert taken.die_cut_pricing.salary == original.die_cut_pricing.salary


def _assert_full_order(
    taken: Order, original: Order, order_id: int
) -> None:
    assert taken.id == order_id
    assert taken.unit_count == original.unit_count
    assert taken.tax_rate == original.tax_rate
    assert taken.markup == original.markup
    assert taken.operation_costs == original.operation_costs
    assert taken.comment == original.comment
    assert len(taken.comment) == 501
    assert taken.status is original.status
    assert len(taken.printings) == len(original.printings)
    for taken_printing, original_printing in zip(
        taken.printings, original.printings, strict=True
    ):
        _assert_printing(taken_printing, original_printing)


def _raises_missing(order_id: int = _MISSING_ID) -> str:
    return re.escape(f"заказа нет, id={order_id}")


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    sync_engine = create_sync_engine()
    try:
        yield sync_engine
    finally:
        sync_engine.dispose()


@pytest.fixture
def repository(
    engine: Engine,
) -> Iterator[tuple[SqlWorkplaceOrderRepository, list[int]]]:
    saved_ids: list[int] = []
    store = SqlWorkplaceOrderRepository(engine)
    try:
        yield store, saved_ids
    finally:
        if not saved_ids:
            return
        statement = text(
            "DELETE FROM workplace_order WHERE id IN :ids"
        ).bindparams(bindparam("ids", expanding=True))
        with engine.begin() as connection:
            connection.execute(statement, {"ids": saved_ids})


def test_order_without_identity_starts_unsaved() -> None:
    order = Order(
        unit_count=1,
        tax_rate=Decimal("0"),
        markup=Decimal("0"),
        operation_costs=(),
        printings=(),
    )
    assert order.id is None
    assert order.comment == ""
    assert order.status is Status.SAVED
    assert {item.name for item in fields(Order)} == {
        "unit_count",
        "tax_rate",
        "markup",
        "operation_costs",
        "printings",
        "id",
        "comment",
        "status",
    }


def test_save_assigns_id_and_stores_no_cost_report(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    store, saved_ids = repository
    order = _full_order()
    order_id = _save(store, saved_ids, order)
    assert type(order_id) is int
    assert order.id is None
    assert store.reports(order_id) == []


def test_take_returns_saved_order(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    store, saved_ids = repository
    order = _full_order()
    order_id = _save(store, saved_ids, order)
    taken = store.take(order_id)
    _assert_full_order(taken, order, order_id)


def test_take_has_no_workplace_report(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    store, saved_ids = repository
    order_id = _save(store, saved_ids, _full_order())
    taken = store.take(order_id)
    for printing in taken.printings:
        for pricing in (
            printing.press_pricing,
            printing.cut_pricing,
            printing.lamination_pricing,
            printing.die_cut_pricing,
        ):
            with pytest.raises(RuntimeError, match="Report is not attach"):
                pricing.calculate()


def test_empty_collections_round_trip(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    store, saved_ids = repository
    order_id = _save(store, saved_ids, _bare_order())
    taken = store.take(order_id)
    assert taken.operation_costs == ()
    assert taken.printings == ()
    assert taken.comment == ""
    assert taken.status is Status.SAVED
    assert taken.id == order_id


def test_save_unknown_id_raises_and_writes_nothing(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, _saved_ids = repository
    before = _count_rows(engine, "workplace_order")
    with pytest.raises(OrderNotFound, match=_raises_missing()):
        store.save(_bare_order(_MISSING_ID))
    assert _count_rows(engine, "workplace_order") == before


def test_second_save_replaces_order_and_keeps_reports(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    store, saved_ids = repository
    order_id = _save(store, saved_ids, _full_order())
    report_a = _report_a()
    report_b = _report_b()
    store.attach(report_a, order_id)
    store.attach(report_b, order_id)
    second = Order(
        unit_count=7,
        tax_rate=Decimal("1"),
        markup=Decimal("0"),
        operation_costs=(),
        printings=(),
        id=order_id,
        comment="второй",
        status=Status.DONE,
    )
    assert store.save(second) == order_id
    taken = store.take(order_id)
    assert taken.id == order_id
    assert taken.comment == "второй"
    assert taken.status is Status.DONE
    assert taken.unit_count == 7
    assert taken.tax_rate == Decimal("1")
    assert taken.markup == Decimal("0")
    assert taken.operation_costs == ()
    assert taken.printings == ()
    assert store.reports(order_id) == [report_a, report_b]


def test_take_unknown_id_raises(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    store, _saved_ids = repository
    with pytest.raises(OrderNotFound, match=_raises_missing()):
        store.take(_MISSING_ID)


def test_attach_unknown_id_raises_and_writes_nothing(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, _saved_ids = repository
    before = _count_rows(engine, "workplace_cost_report")
    with pytest.raises(OrderNotFound, match=_raises_missing()):
        store.attach(_report_a(), _MISSING_ID)
    assert _count_rows(engine, "workplace_cost_report") == before


def test_reports_return_attached_reports_in_call_order(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    store, saved_ids = repository
    order_id = _save(store, saved_ids, _full_order())
    report_a = _report_a()
    report_b = _report_b()
    store.attach(report_a, order_id)
    store.attach(report_b, order_id)
    found = store.reports(order_id)
    assert found == [report_a, report_b]
    assert found[1].printing_cost_reports == ()


def test_attach_keeps_report_when_printing_cost_count_differs(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    store, saved_ids = repository
    order = Order(
        unit_count=1,
        tax_rate=Decimal("0"),
        markup=Decimal("0"),
        operation_costs=(),
        printings=(_full_order().printings[0],),
    )
    order_id = _save(store, saved_ids, order)
    report = _report_b()
    store.attach(report, order_id)
    found = store.reports(order_id)
    assert found == [report]
    assert found[0].printing_cost_reports == ()


def test_reports_empty_without_attach(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    store, saved_ids = repository
    order_id = _save(store, saved_ids, _bare_order())
    assert store.reports(order_id) == []


def test_reports_unknown_id_raises(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    store, _saved_ids = repository
    with pytest.raises(OrderNotFound, match=_raises_missing()):
        store.reports(_MISSING_ID)


def test_upgrade_adds_workplace_tables_and_keeps_old_order_rows(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, saved_ids = repository
    names = _public_table_names(engine)
    for name in (
        "workplace_order",
        "workplace_operation_cost",
        "workplace_printing",
        "workplace_cost_report",
        "workplace_printing_cost",
        "order",
    ):
        assert name in names
    before = _count_rows(engine, '"order"')
    _save(store, saved_ids, _bare_order())
    assert _count_rows(engine, '"order"') == before
