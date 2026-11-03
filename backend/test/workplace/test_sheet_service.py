import threading
from collections.abc import Callable, Iterator
from decimal import Decimal

import pytest
from sqlalchemy import bindparam, text
from sqlalchemy.engine import Engine

from backend.core.accountant.money import Money
from backend.core.sheet.format import SheetFormat, standard_formats
from backend.core.sheet.repository import SheetSizeRejected
from backend.core.sheet.service import SaveSheet, SheetService
from backend.core.sheet.sheet import Sheet
from backend.storage.repositories.sheet_repository import SqlSheetRepository
from backend.storage.sync_engine import create_sync_engine

_A4 = standard_formats()[3]


def _rate(amount: str) -> Money:
    return Money(Decimal(amount))


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


def _tuple_count(
    engine: Engine,
    height: int,
    width: int,
    density: int,
    cost: Money,
) -> int:
    with engine.connect() as connection:
        count = connection.execute(
            text(
                "SELECT count(*) FROM sheet "
                "WHERE height = :height AND width = :width "
                "AND density = :density AND cost = :cost"
            ),
            {
                "height": height,
                "width": width,
                "density": density,
                "cost": cost.amount,
            },
        ).scalar_one()
    return int(count)


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    sync_engine = create_sync_engine()
    try:
        yield sync_engine
    finally:
        sync_engine.dispose()


@pytest.fixture
def catalog(
    engine: Engine,
) -> Iterator[tuple[SheetService, SqlSheetRepository, list[int]]]:
    saved: list[int] = []
    repository = SqlSheetRepository(engine)
    service = SheetService(repository)
    try:
        yield service, repository, saved
    finally:
        if not saved:
            return
        statement = text(
            "DELETE FROM sheet WHERE id IN :ids"
        ).bindparams(bindparam("ids", expanding=True))
        with engine.begin() as connection:
            connection.execute(statement, {"ids": saved})


def test_should_keep_one_row_when_two_saves_of_one_tuple_run_together(
    catalog: tuple[SheetService, SqlSheetRepository, list[int]],
    engine: Engine,
) -> None:
    service, repository, saved = catalog
    cost = _rate("1.01")
    command = SaveSheet(None, _A4.height, _A4.width, 810001, cost)
    found: list[int | None] = [None, None]

    def save_at(index: int) -> None:
        found[index] = service.save(command)

    try:
        outcomes = _run_together(
            lambda: save_at(0), lambda: save_at(1)
        )
        assert outcomes == [None, None]
        assert found[0] == found[1]
        assert type(found[0]) is int
        saved.append(found[0])
        assert _tuple_count(
            engine, _A4.height, _A4.width, 810001, cost
        ) == 1
        taken = repository.take(found[0])
        assert taken.format.name == _A4.name
        assert taken.format.height == _A4.height
        assert taken.format.width == _A4.width
        assert taken.density == 810001
        assert taken.cost == cost
        assert taken.version == 0
    finally:
        for item in found:
            if type(item) is int and item not in saved:
                saved.append(item)


def test_should_return_the_moved_sheet_without_renaming_it(
    catalog: tuple[SheetService, SqlSheetRepository, list[int]],
) -> None:
    service, repository, saved = catalog
    cost = _rate("1.02")
    sheet_id = repository.save(
        Sheet(SheetFormat("210 x 297", 210, 297), 810002, cost)
    )
    saved.append(sheet_id)
    again = service.save(SaveSheet(None, 210, 297, 810002, cost))
    assert again == sheet_id
    taken = repository.take(sheet_id)
    assert taken.format.name == "210 x 297"
    assert taken.format.height == 210
    assert taken.format.width == 297
    assert taken.density == 810002
    assert taken.cost == cost
    assert taken.version == 0


@pytest.mark.parametrize(("height", "width"), [(450, 320), (297, 210)])
def test_should_reject_a_size_that_is_not_a_factory_format(
    catalog: tuple[SheetService, SqlSheetRepository, list[int]],
    engine: Engine,
    height: int,
    width: int,
) -> None:
    service, _repository, _saved = catalog
    cost = _rate("1.06")
    before = _tuple_count(engine, height, width, 810006, cost)
    with pytest.raises(SheetSizeRejected) as caught:
        service.save(SaveSheet(None, height, width, 810006, cost))
    assert str(caught.value) == "save: высота и ширина не из фабрики"
    assert _tuple_count(engine, height, width, 810006, cost) == before


def test_should_reprice_a_stored_sheet_and_keep_its_format(
    catalog: tuple[SheetService, SqlSheetRepository, list[int]],
) -> None:
    service, repository, saved = catalog
    sheet_id = service.save(
        SaveSheet(None, 210, 297, 810003, _rate("1.03"))
    )
    saved.append(sheet_id)
    assert service.save(
        SaveSheet(sheet_id, 450, 320, 810013, _rate("2.03"))
    ) == sheet_id
    taken = repository.take(sheet_id)
    assert taken.format.name == _A4.name
    assert taken.format.height == 210
    assert taken.format.width == 297
    assert taken.density == 810013
    assert taken.cost == _rate("2.03")
    assert taken.version == 1
    assert service.save(
        SaveSheet(sheet_id, 1, 1, 810013, _rate("2.03"))
    ) == sheet_id
    assert repository.take(sheet_id).version == 1
