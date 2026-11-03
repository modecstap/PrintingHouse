import json
import re
import threading
from collections.abc import Callable, Iterator
from dataclasses import fields
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.engine import Engine

from backend.core.accountant.money import Money
from backend.core.accountant.pricing.cutting import CuttingCalculation
from backend.core.accountant.pricing.die_cutting import (
    DieCuttingCalculation,
)
from backend.core.accountant.pricing.lamination import (
    LaminationCalculation,
)
from backend.core.accountant.pricing.printing import PrintingCalculation
from backend.core.order import (
    List,
    Operation,
    Order,
    OrderSpecification,
    Printing,
    PrintingSpecification,
    Status,
)
from backend.core.order_repository import (
    OrderNotFound,
    OrderStoreUnavailable,
)
from backend.core.sheet.repository import SheetNotFound
from backend.core.reports import CostReport, PrintingCost
from backend.core.workplaces.lamination.models import Lamination
from backend.core.workplaces.printing.models import Chroma
from backend.storage.repositories.workplace_order_repository import (
    SqlWorkplaceOrderRepository,
)
from backend.storage.sync_engine import create_sync_engine

_MISSING_ID = 9_000_000_000_001


def _money(amount: Decimal) -> Money:
    return Money(amount)


def _order(
    unit_count: int,
    tax_rate: Decimal,
    markup: Decimal,
    operations: tuple[Operation, ...],
    printings: tuple[Printing, ...],
    order_id: int | None = None,
    comment: str = "",
    status: Status = Status.SAVED,
) -> Order:
    return Order(
        specification=OrderSpecification(unit_count, markup, operations),
        tax_rate=tax_rate,
        printings=printings,
        id=order_id,
        comment=comment,
        status=status,
    )


def _sheet_id(
    engine: Engine,
    name: str,
    height: int,
    width: int,
    density: int,
    cost: Decimal,
) -> int:
    params = {
        "name": name,
        "height": height,
        "width": width,
        "density": density,
        "cost": cost,
    }
    insert_sheet = text(
        "INSERT INTO sheet (version, name, height, width, density, cost) "
        "VALUES (0, :name, :height, :width, :density, :cost) "
        "ON CONFLICT (height, width, density, cost) DO NOTHING "
        "RETURNING id"
    )
    select_sheet = text(
        "SELECT id FROM sheet "
        "WHERE height = :height AND width = :width "
        "AND density = :density AND cost = :cost"
    )
    with engine.begin() as connection:
        inserted = connection.execute(insert_sheet, params).scalar_one_or_none()
        if inserted is not None:
            return int(inserted)
        return int(connection.execute(select_sheet, params).scalar_one())


def _printing(
    count: int,
    chroma: Chroma,
    lamination: Lamination,
    die_cutting: bool,
    stack_height: int,
    spacing: int,
    density: int,
    width: int,
    height: int,
    press_sheet: int,
    paper: Decimal,
    sheet: List,
    press: tuple[Decimal, Decimal, Decimal, Decimal, Decimal],
    cut: Decimal,
    lamination_rates: tuple[Decimal, Decimal, Decimal],
    die_cut: Decimal,
    comment: str = "",
) -> Printing:
    startup, film_cost, salary = lamination_rates
    return Printing(
        specification=PrintingSpecification(
            count=count,
            chroma=chroma,
            lamination=lamination,
            die_cutting=die_cutting,
            spacing=spacing,
            press_sheet=press_sheet,
            list=sheet,
        ),
        stack_height=stack_height,
        press_pricing=PrintingCalculation(
            _money(press[0]),
            _money(press[1]),
            _money(press[2]),
            _money(press[3]),
            _money(press[4]),
        ),
        cut_pricing=CuttingCalculation(_money(cut)),
        lamination_pricing=LaminationCalculation(
            _money(startup),
            _money(film_cost),
            _money(salary),
        ),
        die_cut_pricing=DieCuttingCalculation(_money(die_cut)),
        comment=comment,
    )


def _full_order(engine: Engine) -> Order:
    zero = Decimal(0)
    first_sheet = _sheet_id(
        engine, "450 x 320", 450, 320, 150, Decimal("5.50")
    )
    second_sheet = _sheet_id(engine, "100 x 100", 100, 100, 80, zero)
    first = _printing(
        3,
        Chroma.FOUR_FOUR,
        Lamination.ONE_ONE,
        True,
        50,
        2,
        150,
        320,
        450,
        first_sheet,
        Decimal("5.50"),
        List(90, 50, 2),
        (
            Decimal("1.10"),
            Decimal("2.20"),
            Decimal("3.30"),
            Decimal("4.40"),
            Decimal("6.60"),
        ),
        Decimal("7.70"),
        (Decimal("200"), Decimal("8.80"), Decimal("9.90")),
        Decimal("10.10"),
        comment="кромка",
    )
    second = _printing(
        1,
        Chroma.ZERO_ZERO,
        Lamination.DONT,
        False,
        1,
        0,
        80,
        100,
        100,
        second_sheet,
        zero,
        List(10, 20, 0),
        (zero, zero, zero, zero, zero),
        zero,
        (zero, zero, zero),
        zero,
    )
    return _order(
        unit_count=12,
        tax_rate=Decimal("0.93"),
        markup=Decimal("20"),
        operations=(
            Operation("", Decimal("10.5"), ""),
            Operation("", Decimal("-1.25"), ""),
        ),
        printings=(first, second),
        comment="а" * 501,
        status=Status.IN_WORK,
    )


def _bare_order(order_id: int | None = None) -> Order:
    return _order(
        unit_count=1,
        tax_rate=Decimal("0"),
        markup=Decimal("0"),
        operations=(),
        printings=(),
        order_id=order_id,
    )


def _sized_order(
    order_id: int, comment: str, printings: tuple[Printing, ...]
) -> Order:
    return _order(
        unit_count=1,
        tax_rate=Decimal("0"),
        markup=Decimal("0"),
        operations=(),
        printings=printings,
        order_id=order_id,
        comment=comment,
    )


def _join_pair(
    first: Callable[[], None], second: Callable[[], None]
) -> None:
    barrier = threading.Barrier(2)
    errors: list[BaseException] = []

    def run(action: Callable[[], None]) -> None:
        try:
            barrier.wait(10)
            action()
        except BaseException as error:
            errors.append(error)

    threads = [
        threading.Thread(target=run, args=(action,), daemon=True)
        for action in (first, second)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(10)
    assert not threads[0].is_alive()
    assert not threads[1].is_alive()
    assert errors == []


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


def _reference_document(engine: Engine) -> object:
    with engine.connect() as connection:
        return connection.execute(
            text(
                "SELECT document FROM reference WHERE id = 1"
            )
        ).scalar_one_or_none()


def _restore_reference(engine: Engine, document: object) -> None:
    with engine.begin() as connection:
        if document is None:
            connection.execute(
                text("DELETE FROM reference WHERE id = 1")
            )
            return
        connection.execute(
            text(
                "INSERT INTO reference (id, document) "
                "VALUES (1, CAST(:document AS jsonb)) "
                "ON CONFLICT (id) DO UPDATE "
                "SET document = EXCLUDED.document"
            ),
            {"document": json.dumps(document)},
        )


def _assert_reference(taken: Order, expected: Order) -> None:
    assert taken.id is None
    assert taken.creation_date is None
    assert taken.specification.unit_count == expected.specification.unit_count
    assert taken.tax_rate == expected.tax_rate
    assert taken.specification.markup == expected.specification.markup
    assert taken.specification.operations == expected.specification.operations
    assert taken.comment == expected.comment
    assert taken.status is expected.status
    assert len(taken.printings) == len(expected.printings)
    for taken_printing, expected_printing in zip(
        taken.printings, expected.printings, strict=True
    ):
        _assert_printing(taken_printing, expected_printing)


def _public_table_names(engine: Engine) -> set[str]:
    query = text(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public'"
    )
    with engine.connect() as connection:
        return set(connection.execute(query).scalars().all())


def _assert_printing(taken: Printing, original: Printing) -> None:
    assert taken.specification == original.specification
    assert taken.stack_height == original.stack_height
    assert taken.press_pricing.cyan == original.press_pricing.cyan
    assert taken.press_pricing.magenta == original.press_pricing.magenta
    assert taken.press_pricing.yellow == original.press_pricing.yellow
    assert taken.press_pricing.black == original.press_pricing.black
    assert taken.specification.press_sheet == original.specification.press_sheet
    assert taken.specification.spacing == original.specification.spacing
    assert taken.press_pricing.salary == original.press_pricing.salary
    assert taken.cut_pricing.salary == original.cut_pricing.salary
    startup = taken.lamination_pricing.startup
    assert startup == original.lamination_pricing.startup
    film_cost = taken.lamination_pricing.film_cost
    assert film_cost == original.lamination_pricing.film_cost
    salary = taken.lamination_pricing.salary
    assert salary == original.lamination_pricing.salary
    assert taken.die_cut_pricing.salary == original.die_cut_pricing.salary
    assert taken.comment == original.comment


def _assert_full_order(
    taken: Order, original: Order, order_id: int
) -> None:
    assert taken.id == order_id
    assert taken.specification.unit_count == original.specification.unit_count
    assert taken.tax_rate == original.tax_rate
    assert taken.specification.markup == original.specification.markup
    assert taken.specification.operations == original.specification.operations
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
            'DELETE FROM "order" WHERE id IN :ids'
        ).bindparams(bindparam("ids", expanding=True))
        with engine.begin() as connection:
            connection.execute(statement, {"ids": saved_ids})


def test_order_without_identity_starts_unsaved() -> None:
    order = _order(
        unit_count=1,
        tax_rate=Decimal("0"),
        markup=Decimal("0"),
        operations=(),
        printings=(),
    )
    assert order.id is None
    assert order.comment == ""
    assert order.status is Status.SAVED
    assert {item.name for item in fields(Order)} == {
        "specification",
        "tax_rate",
        "printings",
        "id",
        "comment",
        "status",
        "creation_date",
    }


def test_save_assigns_id_and_stores_no_cost_report(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, saved_ids = repository
    order = _full_order(engine)
    order_id = _save(store, saved_ids, order)
    assert type(order_id) is int
    assert order.id is None
    assert store.reports(order_id) == []


def test_take_returns_saved_order(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, saved_ids = repository
    order = _full_order(engine)
    order_id = _save(store, saved_ids, order)
    taken = store.take(order_id)
    _assert_full_order(taken, order, order_id)


def test_take_has_no_workplace_report(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, saved_ids = repository
    order_id = _save(store, saved_ids, _full_order(engine))
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
    assert taken.specification.operations == ()
    assert taken.printings == ()
    assert taken.comment == ""
    assert taken.status is Status.SAVED
    assert taken.id == order_id


def test_should_refuse_an_unknown_sheet_and_write_no_order(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, _saved_ids = repository
    printing = _printing(
        1,
        Chroma.ZERO_ZERO,
        Lamination.DONT,
        False,
        1,
        0,
        0,
        1,
        1,
        _MISSING_ID,
        Decimal(0),
        List(1, 1, 0),
        (Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0)),
        Decimal(0),
        (Decimal(0), Decimal(0), Decimal(0)),
        Decimal(0),
    )
    order = _order(
        unit_count=1,
        tax_rate=Decimal(0),
        markup=Decimal(0),
        operations=(),
        printings=(printing,),
    )
    before = _count_rows(engine, '"order"')
    with pytest.raises(SheetNotFound) as caught:
        store.save(order)
    assert str(caught.value) == f"save: листа нет, id={_MISSING_ID}"
    assert caught.value.__cause__ is not None
    assert "postgres" not in str(caught.value)
    assert _count_rows(engine, '"order"') == before


def test_save_unknown_id_raises_and_writes_nothing(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, _saved_ids = repository
    before = _count_rows(engine, '"order"')
    with pytest.raises(OrderNotFound, match=_raises_missing()):
        store.save(_bare_order(_MISSING_ID))
    assert _count_rows(engine, '"order"') == before


def test_second_save_replaces_order_and_keeps_reports(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, saved_ids = repository
    order_id = _save(store, saved_ids, _full_order(engine))
    created_on = store.take(order_id).creation_date
    report_a = _report_a()
    report_b = _report_b()
    store.attach(report_a, order_id)
    store.attach(report_b, order_id)
    second = _order(
        unit_count=7,
        tax_rate=Decimal("1"),
        markup=Decimal("0"),
        operations=(),
        printings=(),
        order_id=order_id,
        comment="второй",
        status=Status.DONE,
    )
    assert store.save(second) == order_id
    taken = store.take(order_id)
    assert taken.id == order_id
    assert taken.creation_date == created_on
    assert created_on == date.today()
    assert taken.comment == "второй"
    assert taken.status is Status.DONE
    assert taken.specification.unit_count == 7
    assert taken.tax_rate == Decimal("1")
    assert taken.specification.markup == Decimal("0")
    assert taken.specification.operations == ()
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
    before = _count_rows(engine, "cost_report")
    with pytest.raises(OrderNotFound, match=_raises_missing()):
        store.attach(_report_a(), _MISSING_ID)
    assert _count_rows(engine, "cost_report") == before


def test_reports_return_attached_reports_in_call_order(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, saved_ids = repository
    order_id = _save(store, saved_ids, _full_order(engine))
    report_a = _report_a()
    report_b = _report_b()
    store.attach(report_a, order_id)
    store.attach(report_b, order_id)
    found = store.reports(order_id)
    assert found == [report_a, report_b]
    assert found[1].printing_cost_reports == ()


def test_attach_keeps_report_when_printing_cost_count_differs(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, saved_ids = repository
    order = _order(
        unit_count=1,
        tax_rate=Decimal("0"),
        markup=Decimal("0"),
        operations=(),
        printings=(_full_order(engine).printings[0],),
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

def test_concurrent_saves_keep_one_complete_order(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, saved_ids = repository
    order_id = _save(store, saved_ids, _bare_order())
    printings = _full_order(engine).printings
    _join_pair(
        lambda: store.save(_sized_order(order_id, "A", printings[:1])),
        lambda: store.save(_sized_order(order_id, "B", printings)),
    )
    taken = store.take(order_id)
    assert taken.comment in {"A", "B"}
    expected = 1 if taken.comment == "A" else 2
    assert len(taken.printings) == expected


def test_concurrent_attaches_keep_both_reports(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    store, saved_ids = repository
    order_id = _save(store, saved_ids, _bare_order())
    report_a = _report_a()
    report_b = _report_b()
    _join_pair(
        lambda: store.attach(report_a, order_id),
        lambda: store.attach(report_b, order_id),
    )
    found = store.reports(order_id)
    assert len(found) == 2
    assert report_a in found
    assert report_b in found


def test_repeated_saves_return_the_connection(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
) -> None:
    _store, saved_ids = repository
    source = create_sync_engine()
    local = create_engine(
        source.url,
        pool_size=1,
        max_overflow=0,
        pool_timeout=2,
    )
    source.dispose()
    store = SqlWorkplaceOrderRepository(local)
    try:
        for _ in range(5):
            order_id = store.save(_bare_order())
            saved_ids.append(order_id)
            assert store.take(order_id).id == order_id
    finally:
        local.dispose()


def test_unreachable_database_is_store_unavailable() -> None:
    local = create_engine(
        "postgresql+psycopg://postgres:secret-token@127.0.0.1:1/postgres",
        connect_args={"connect_timeout": 2},
    )
    try:
        store = SqlWorkplaceOrderRepository(local)
        order = _order(
            unit_count=1,
            tax_rate=Decimal("0"),
            markup=Decimal("0"),
            operations=(),
            printings=(),
            comment="order-body-marker",
        )
        with pytest.raises(OrderStoreUnavailable) as caught:
            store.save(order)
        error = caught.value
        assert error.__cause__ is not None
        assert type(error) is not OrderNotFound
        assert type(error.__cause__) is not OrderNotFound
        message = str(error)
        assert "secret-token" not in message
        assert "127.0.0.1" not in message
        assert "postgresql" not in message
        assert "order-body-marker" not in message
    finally:
        local.dispose()


def test_should_keep_one_complete_reference_when_two_writes_race(
    repository: tuple[SqlWorkplaceOrderRepository, list[int]],
    engine: Engine,
) -> None:
    store, _saved_ids = repository
    full = _full_order(engine)
    left = _order(
        unit_count=2,
        tax_rate=Decimal("0.1"),
        markup=Decimal("1"),
        operations=(Operation("рез", Decimal("3"), "кромка"),),
        printings=full.printings[:1],
        comment="A",
        status=Status.IN_WORK,
    )
    right = _order(
        unit_count=9,
        tax_rate=Decimal("0.2"),
        markup=Decimal("4"),
        operations=(
            Operation("биговка", Decimal("0"), ""),
            Operation("рез", Decimal("-1.25"), "вторая"),
        ),
        printings=full.printings,
        comment="B",
        status=Status.DONE,
    )
    previous = _reference_document(engine)
    before = _count_rows(engine, '"order"')
    try:
        _join_pair(
            lambda: store.set_reference(left),
            lambda: store.set_reference(right),
        )
        taken = store.reference()
        assert taken is not None
        assert taken.comment in {"A", "B"}
        expected = left if taken.comment == "A" else right
        _assert_reference(taken, expected)
        assert _count_rows(engine, '"order"') == before
    finally:
        _restore_reference(engine, previous)
