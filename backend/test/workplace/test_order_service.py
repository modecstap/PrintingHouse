import threading
from collections.abc import Callable, Iterator
from dataclasses import replace
from decimal import Decimal, InvalidOperation

import pytest
from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.engine import Engine

from backend.workplace.administrator import Administrator
from backend.workplace.cost_order import Order, Status
from backend.workplace.order_repository import (
    OrderNotFound,
    OrderStoreUnavailable,
)
from backend.workplace.order_service import WorkplaceOrderService
from backend.workplace.reports import CostReport
from backend.workplace_order_db import (
    SqlWorkplaceOrderRepository,
    create_sync_engine,
)

_MISSING_ID = 9_000_000_000_001
_MISSING_TEXT = f"заказа нет, id={_MISSING_ID}"

_ZERO_REPORT = CostReport(
    Decimal("0.00"),
    Decimal("0.00"),
    Decimal("0.00"),
    Decimal("0.00"),
    (),
)
_OPERATION_REPORT = CostReport(
    Decimal("3.00"),
    Decimal("3.00"),
    Decimal("6.00"),
    Decimal("0.00"),
    (),
)

_Bundle = tuple[
    WorkplaceOrderService, SqlWorkplaceOrderRepository, list[int]
]


def _order(
    *,
    unit_count: int = 1,
    operation_costs: tuple[Decimal, ...] = (),
    order_id: int | None = None,
    comment: str = "",
    status: Status = Status.SAVED,
) -> Order:
    return Order(
        unit_count=unit_count,
        tax_rate=Decimal("1"),
        markup=Decimal("0"),
        operation_costs=operation_costs,
        printings=(),
        id=order_id,
        comment=comment,
        status=status,
    )


def _operation_order(
    *,
    order_id: int | None = None,
    comment: str = "",
    status: Status = Status.SAVED,
) -> Order:
    return _order(
        unit_count=2,
        operation_costs=(Decimal("3"),),
        order_id=order_id,
        comment=comment,
        status=status,
    )


def _call(
    service: WorkplaceOrderService, keep: str, order: Order
) -> tuple[int, CostReport]:
    if keep == "accept":
        return service.accept(order)
    if keep == "delay":
        return service.delay(order)
    raise AssertionError(keep)


def _count_rows(engine: Engine, table: str) -> int:
    with engine.connect() as connection:
        count = connection.execute(
            text(f"SELECT count(*) FROM {table}")
        ).scalar_one()
    return int(count)


def _order_and_report_counts(engine: Engine) -> tuple[int, int]:
    return (
        _count_rows(engine, "workplace_order"),
        _count_rows(engine, "workplace_cost_report"),
    )


def _run_together(
    first: Callable[[], None], second: Callable[[], None]
) -> list[BaseException | None]:
    barrier = threading.Barrier(2)
    outcomes: list[BaseException | None] = [None, None]

    def run(index: int, action: Callable[[], None]) -> None:
        try:
            barrier.wait(10)
            action()
        except BaseException as error:
            outcomes[index] = error

    threads = [
        threading.Thread(target=run, args=(0, first), daemon=True),
        threading.Thread(target=run, args=(1, second), daemon=True),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(10)
    assert not threads[0].is_alive()
    assert not threads[1].is_alive()
    return outcomes


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    sync_engine = create_sync_engine()
    try:
        yield sync_engine
    finally:
        sync_engine.dispose()


@pytest.fixture
def workplace(
    engine: Engine,
) -> Iterator[_Bundle]:
    saved_ids: list[int] = []
    orders = SqlWorkplaceOrderRepository(engine)
    service = WorkplaceOrderService(orders, Administrator())
    try:
        yield service, orders, saved_ids
    finally:
        if not saved_ids:
            return
        statement = text(
            "DELETE FROM workplace_order WHERE id IN :ids"
        ).bindparams(bindparam("ids", expanding=True))
        with engine.begin() as connection:
            connection.execute(statement, {"ids": saved_ids})


def test_should_save_a_new_order_and_return_its_id(
    workplace: _Bundle,
) -> None:
    service, orders, saved_ids = workplace
    order = _order(status=Status.DONE, comment="заметка")
    held = replace(order)
    order_id = service.save(order)
    saved_ids.append(order_id)
    assert type(order_id) is int
    assert order == held
    assert order.id is None
    taken = service.take(order_id)
    assert taken.comment == "заметка"
    assert taken.status is Status.DONE
    assert taken.unit_count == 1
    assert taken.operation_costs == ()
    assert orders.reports(order_id) == []


def test_should_update_the_same_order_on_a_second_save(
    workplace: _Bundle,
) -> None:
    service, orders, saved_ids = workplace
    first = _order(comment="было", status=Status.SAVED)
    held_first = replace(first)
    order_id = service.save(first)
    saved_ids.append(order_id)
    assert first == held_first
    second = _order(
        order_id=order_id, comment="стало", status=Status.DONE
    )
    held_second = replace(second)
    updated_id = service.save(second)
    assert updated_id == order_id
    assert second == held_second
    taken = service.take(order_id)
    assert taken.comment == "стало"
    assert taken.status is Status.DONE
    assert orders.reports(order_id) == []


def test_should_refuse_to_save_an_unknown_id(
    workplace: _Bundle, engine: Engine
) -> None:
    service, _orders, _saved_ids = workplace
    order = _order(order_id=_MISSING_ID)
    held = replace(order)
    before = _count_rows(engine, "workplace_order")
    with pytest.raises(OrderNotFound, match=_MISSING_TEXT):
        service.save(order)
    assert _count_rows(engine, "workplace_order") == before
    assert order == held


def test_should_return_one_saved_order_from_take(
    workplace: _Bundle,
) -> None:
    service, orders, saved_ids = workplace
    order = _order(status=Status.DONE, comment="заметка")
    held = replace(order)
    order_id = service.save(order)
    saved_ids.append(order_id)
    assert order == held
    taken = service.take(order_id)
    assert type(taken) is Order
    assert taken.id == order_id
    assert taken.comment == "заметка"
    assert taken.status is Status.DONE
    assert taken.unit_count == order.unit_count
    assert taken.tax_rate == order.tax_rate
    assert taken.markup == order.markup
    assert taken.operation_costs == ()
    assert taken.printings == ()
    assert orders.reports(order_id) == []


def test_should_refuse_to_take_an_unknown_id(
    workplace: _Bundle,
) -> None:
    service, _orders, _saved_ids = workplace
    with pytest.raises(OrderNotFound, match=_MISSING_TEXT):
        service.take(_MISSING_ID)


def test_should_list_orders_with_the_larger_id_first(
    workplace: _Bundle,
) -> None:
    service, _orders, saved_ids = workplace
    first_id = service.save(_order(comment="первый"))
    second_id = service.save(_order(comment="второй"))
    saved_ids.append(first_id)
    saved_ids.append(second_id)
    listed_ids = [item.id for item in service.take_all()]
    assert listed_ids.count(first_id) == 1
    assert listed_ids.count(second_id) == 1
    larger = max(first_id, second_id)
    smaller = min(first_id, second_id)
    assert listed_ids.index(larger) < listed_ids.index(smaller)


def test_should_delete_an_order_and_its_report(
    workplace: _Bundle,
) -> None:
    service, orders, saved_ids = workplace
    first = _order(comment="первый", status=Status.DONE)
    held_first = replace(first)
    first_id, _report = service.accept(first)
    saved_ids.append(first_id)
    assert first == held_first
    second = _order(comment="второй", status=Status.SAVED)
    held_second = replace(second)
    second_id = service.save(second)
    saved_ids.append(second_id)
    assert second == held_second
    service.delete(first_id)
    with pytest.raises(OrderNotFound):
        service.take(first_id)
    with pytest.raises(OrderNotFound):
        orders.reports(first_id)
    taken = service.take(second_id)
    assert taken.id == second_id
    assert taken.comment == "второй"


def test_should_refuse_to_delete_an_unknown_id(
    workplace: _Bundle, engine: Engine
) -> None:
    service, _orders, _saved_ids = workplace
    before = _order_and_report_counts(engine)
    with pytest.raises(OrderNotFound, match=_MISSING_TEXT):
        service.delete(_MISSING_ID)
    assert _order_and_report_counts(engine) == before


def test_should_return_the_calculated_report_and_write_nothing(
    workplace: _Bundle, engine: Engine
) -> None:
    service, _orders, _saved_ids = workplace
    empty = _order()
    held_empty = replace(empty)
    with_operation = _operation_order()
    held_operation = replace(with_operation)
    before = _order_and_report_counts(engine)
    assert service.calculate(empty) == _ZERO_REPORT
    assert service.calculate(with_operation) == _OPERATION_REPORT
    assert empty == held_empty
    assert with_operation == held_operation
    assert _order_and_report_counts(engine) == before


def test_should_let_a_calculation_error_reach_the_caller(
    workplace: _Bundle, engine: Engine
) -> None:
    service, _orders, _saved_ids = workplace
    order = _order(unit_count=0)
    held = replace(order)
    before = _order_and_report_counts(engine)
    with pytest.raises(InvalidOperation):
        service.calculate(order)
    assert order == held
    assert _order_and_report_counts(engine) == before


@pytest.mark.parametrize(
    ("keep", "incoming", "stored"),
    [
        ("accept", Status.DONE, Status.IN_WORK),
        ("delay", Status.IN_WORK, Status.SAVED),
    ],
)
def test_should_accept_or_delay_and_attach_that_report(
    workplace: _Bundle,
    keep: str,
    incoming: Status,
    stored: Status,
) -> None:
    service, orders, saved_ids = workplace
    order = _order(comment="заметка", status=incoming)
    held = replace(order)
    order_id, report = _call(service, keep, order)
    saved_ids.append(order_id)
    assert type(order_id) is int
    assert report == _ZERO_REPORT
    assert order == held
    taken = service.take(order_id)
    assert taken.comment == "заметка"
    assert taken.unit_count == 1
    assert taken.status is stored
    assert orders.reports(order_id) == [_ZERO_REPORT]


@pytest.mark.parametrize("keep", ["accept", "delay"])
def test_should_write_nothing_when_accept_or_delay_cannot_calculate(
    workplace: _Bundle, engine: Engine, keep: str
) -> None:
    service, _orders, _saved_ids = workplace
    order = _order(unit_count=0)
    held = replace(order)
    before = _order_and_report_counts(engine)
    with pytest.raises(InvalidOperation):
        _call(service, keep, order)
    assert _order_and_report_counts(engine) == before
    assert order == held
    assert order.id is None


@pytest.mark.parametrize("keep", ["accept", "delay"])
def test_should_keep_a_saved_order_when_a_later_accept_or_delay_cannot_calculate(
    workplace: _Bundle, keep: str
) -> None:
    service, orders, saved_ids = workplace
    saved = _order(comment="keep", status=Status.DONE)
    held_saved = replace(saved)
    order_id = service.save(saved)
    saved_ids.append(order_id)
    assert saved == held_saved
    broken = _order(
        unit_count=0, order_id=order_id, comment="keep", status=Status.DONE
    )
    held_broken = replace(broken)
    with pytest.raises(InvalidOperation):
        _call(service, keep, broken)
    assert broken == held_broken
    taken = service.take(order_id)
    assert taken.unit_count == 1
    assert taken.comment == "keep"
    assert taken.status is Status.DONE
    assert orders.reports(order_id) == []


@pytest.mark.parametrize(
    ("keep", "stored"),
    [
        ("accept", Status.IN_WORK),
        ("delay", Status.SAVED),
    ],
)
def test_should_append_a_report_when_the_same_order_is_accepted_or_delayed_again(
    workplace: _Bundle, keep: str, stored: Status
) -> None:
    service, orders, saved_ids = workplace
    first = _order()
    held_first = replace(first)
    order_id, first_report = _call(service, keep, first)
    saved_ids.append(order_id)
    assert first == held_first
    assert first.id is None
    assert first_report == _ZERO_REPORT
    second = _operation_order(order_id=order_id)
    held_second = replace(second)
    again_id, second_report = _call(service, keep, second)
    assert again_id == order_id
    assert second == held_second
    assert second_report == _OPERATION_REPORT
    assert orders.reports(order_id) == [
        _ZERO_REPORT,
        _OPERATION_REPORT,
    ]
    taken = service.take(order_id)
    assert taken.unit_count == 2
    assert taken.status is stored


@pytest.mark.parametrize("keep", ["accept", "delay"])
def test_should_refuse_to_accept_or_delay_an_unknown_id(
    workplace: _Bundle, engine: Engine, keep: str
) -> None:
    service, _orders, _saved_ids = workplace
    order = _order(order_id=_MISSING_ID)
    held = replace(order)
    before = _order_and_report_counts(engine)
    with pytest.raises(OrderNotFound, match=_MISSING_TEXT):
        _call(service, keep, order)
    assert _order_and_report_counts(engine) == before
    assert order == held


def test_should_change_only_the_status(workplace: _Bundle) -> None:
    service, orders, saved_ids = workplace
    order = _operation_order(comment="заметка")
    held = replace(order)
    order_id, report = service.accept(order)
    saved_ids.append(order_id)
    assert order == held
    assert report == _OPERATION_REPORT
    stored_costs = order.operation_costs
    stored_comment = order.comment
    stored_reports = orders.reports(order_id)
    assert stored_reports == [_OPERATION_REPORT]
    service.change_status(order_id, Status.DONE)
    taken = service.take(order_id)
    assert taken.status is Status.DONE
    assert taken.operation_costs == stored_costs
    assert taken.comment == stored_comment
    assert taken.unit_count == 2
    assert orders.reports(order_id) == stored_reports


def test_should_change_status_without_calculating(
    workplace: _Bundle,
) -> None:
    service, _orders, saved_ids = workplace
    order = _order(unit_count=0)
    held = replace(order)
    order_id = service.save(order)
    saved_ids.append(order_id)
    assert order == held
    service.change_status(order_id, Status.DONE)
    taken = service.take(order_id)
    assert taken.status is Status.DONE
    assert taken.unit_count == 0


def test_should_refuse_to_change_status_of_an_unknown_id(
    workplace: _Bundle, engine: Engine
) -> None:
    service, _orders, _saved_ids = workplace
    before = _count_rows(engine, "workplace_order")
    with pytest.raises(OrderNotFound, match=_MISSING_TEXT):
        service.change_status(_MISSING_ID, Status.DONE)
    assert _count_rows(engine, "workplace_order") == before


def test_should_calculate_without_using_the_database() -> None:
    local = create_engine(
        "postgresql+psycopg://postgres:secret-token@127.0.0.1:1/postgres",
        connect_args={"connect_timeout": 2},
    )
    try:
        service = WorkplaceOrderService(
            SqlWorkplaceOrderRepository(local), Administrator()
        )
        order = _order()
        held = replace(order)
        assert service.calculate(order) == _ZERO_REPORT
        assert order == held
    finally:
        local.dispose()


def test_should_keep_both_reports_when_two_accepts_run_together(
    workplace: _Bundle,
) -> None:
    service, orders, saved_ids = workplace
    order_id = service.save(_order())
    saved_ids.append(order_id)

    def accept_saved() -> None:
        service.accept(_order(order_id=order_id))

    outcomes = _run_together(accept_saved, accept_saved)
    assert outcomes == [None, None]
    assert orders.reports(order_id) == [_ZERO_REPORT, _ZERO_REPORT]
    taken = service.take(order_id)
    assert taken.status is Status.IN_WORK
    assert taken.unit_count == 1
    assert taken.tax_rate == Decimal("1")
    assert taken.markup == Decimal("0")
    assert taken.operation_costs == ()
    assert taken.printings == ()


def test_should_leave_no_order_when_two_deletes_run_together(
    workplace: _Bundle,
) -> None:
    service, _orders, saved_ids = workplace
    order_id = service.save(_order())
    saved_ids.append(order_id)
    outcomes = _run_together(
        lambda: service.delete(order_id),
        lambda: service.delete(order_id),
    )
    failures = [item for item in outcomes if item is not None]
    assert len(failures) == 1
    assert isinstance(failures[0], OrderNotFound)
    assert outcomes.count(None) == 1
    with pytest.raises(OrderNotFound):
        service.take(order_id)


def test_should_return_the_connection(workplace: _Bundle) -> None:
    _service, _orders, saved_ids = workplace
    source = create_sync_engine()
    local = create_engine(
        source.url,
        pool_size=1,
        max_overflow=0,
        pool_timeout=2,
    )
    source.dispose()
    service = WorkplaceOrderService(
        SqlWorkplaceOrderRepository(local), Administrator()
    )
    try:
        for _ in range(3):
            saved_id = service.save(_order())
            saved_ids.append(saved_id)
            accepted_id, _report = service.accept(_order())
            saved_ids.append(accepted_id)
            service.take_all()
            service.delete(saved_id)
            service.delete(accepted_id)
    finally:
        local.dispose()


def test_should_report_an_unreachable_database_without_secrets() -> None:
    local = create_engine(
        "postgresql+psycopg://postgres:secret-token@127.0.0.1:1/postgres",
        connect_args={"connect_timeout": 2},
    )
    try:
        service = WorkplaceOrderService(
            SqlWorkplaceOrderRepository(local), Administrator()
        )
        calls: list[Callable[[], object]] = [
            lambda: service.save(_order()),
            lambda: service.delete(_MISSING_ID),
            lambda: service.take_all(),
            lambda: service.accept(_order(comment="order-body-marker")),
        ]
        for call in calls:
            with pytest.raises(OrderStoreUnavailable) as caught:
                call()
            error = caught.value
            assert error.__cause__ is not None
            assert type(error) is not OrderNotFound
            message = str(error)
            assert "secret-token" not in message
            assert "127.0.0.1" not in message
            assert "postgresql" not in message
            assert "order-body-marker" not in message
    finally:
        local.dispose()
