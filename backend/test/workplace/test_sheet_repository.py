import inspect
import json
from collections.abc import Iterator
from decimal import Decimal

import pytest
from sqlalchemy import bindparam, text
from sqlalchemy.engine import Engine

from backend.core.accountant.money import Money
from backend.core.accountant.pricing.cutting import CuttingCalculation
from backend.core.accountant.pricing.die_cutting import DieCuttingCalculation
from backend.core.accountant.pricing.lamination import LaminationCalculation
from backend.core.accountant.pricing.printing import PrintingCalculation
from backend.core.order import (
    List,
    Order,
    OrderSpecification,
    Printing,
    PrintingSpecification,
    StoredPress,
)
from backend.core.sheet.format import SheetFormat
from backend.core.sheet.repository import (
    SheetInUse,
    SheetNotFound,
    SheetVersionConflict,
)
from backend.core.sheet.sheet import Sheet
from backend.core.workplaces.lamination.models import Lamination
from backend.core.workplaces.printing.models import Chroma
from backend.storage.repositories.sheet_repository import SqlSheetRepository
from backend.storage.repositories.workplace_order_repository import (
    SqlWorkplaceOrderRepository,
)
from backend.storage.sync_engine import create_sync_engine

_MISSING_ID = 9_000_000_000_001


def _rate(amount: str) -> Money:
    return Money(Decimal(amount))


def _new_sheet(
    repository: SqlSheetRepository, saved: list[int]
) -> int:
    sheet_id = repository.save(
        Sheet(SheetFormat("450 x 320", 450, 320), 150, _rate("10"))
    )
    saved.append(sheet_id)
    return sheet_id


def _linked_order(sheet_id: int) -> Order:
    rate = _rate("0")
    printing = Printing(
        specification=PrintingSpecification(
            count=1,
            chroma=Chroma.ZERO_ZERO,
            lamination=Lamination.DONT,
            die_cutting=False,
            spacing=4,
            press_sheet=sheet_id,
            list=List(10, 20, 0),
            sheet_by_fitting=0,
        ),
        stack_height=1,
        press_pricing=PrintingCalculation(rate, rate, rate, rate, rate),
        cut_pricing=CuttingCalculation(rate),
        lamination_pricing=LaminationCalculation(rate, rate, rate),
        die_cut_pricing=DieCuttingCalculation(rate),
        stored_press=StoredPress(0, 0, 0, rate),
    )
    return Order(
        specification=OrderSpecification(1, Decimal(0), ()),
        tax_rate=Decimal(0),
        printings=(printing,),
    )


def _reference_document(engine: Engine) -> object:
    with engine.connect() as connection:
        return connection.execute(
            text("SELECT document FROM reference WHERE id = 1")
        ).scalar_one_or_none()


def _restore_reference(engine: Engine, document: object) -> None:
    with engine.begin() as connection:
        if document is None:
            connection.execute(text("DELETE FROM reference WHERE id = 1"))
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
) -> Iterator[tuple[SqlSheetRepository, list[int]]]:
    saved: list[int] = []
    repository = SqlSheetRepository(engine)
    try:
        yield repository, saved
    finally:
        if not saved:
            return
        statement = text(
            "DELETE FROM sheet WHERE id IN :ids"
        ).bindparams(bindparam("ids", expanding=True))
        with engine.begin() as connection:
            connection.execute(statement, {"ids": saved})


def test_should_store_a_new_sheet_and_return_its_id(
    catalog: tuple[SqlSheetRepository, list[int]],
) -> None:
    repository, saved = catalog
    sheet_id = _new_sheet(repository, saved)
    taken = repository.take(sheet_id)
    assert type(sheet_id) is int
    assert taken.id == sheet_id
    assert taken.version == 0
    assert taken.format.name == "450 x 320"
    assert taken.format.height == 450
    assert taken.format.width == 320
    assert taken.density == 150
    assert taken.cost == _rate("10")


def test_should_update_density_and_cost_and_keep_the_format(
    catalog: tuple[SqlSheetRepository, list[int]],
) -> None:
    repository, saved = catalog
    sheet_id = _new_sheet(repository, saved)
    current = repository.take(sheet_id)
    current.reprice(180, _rate("2"))
    current.format = SheetFormat("чужое", 1, 2)
    assert repository.save(current) == sheet_id
    seen = repository.take(sheet_id)
    assert seen.density == 180
    assert seen.cost == _rate("2")
    assert seen.version == 1
    assert seen.format.name == "450 x 320"
    assert seen.format.height == 450
    assert seen.format.width == 320


def test_should_keep_the_sheet_when_the_version_is_stale(
    catalog: tuple[SqlSheetRepository, list[int]],
) -> None:
    repository, saved = catalog
    sheet_id = _new_sheet(repository, saved)
    current = repository.take(sheet_id)
    current.reprice(180, _rate("2"))
    repository.save(current)
    stale = repository.take(sheet_id)
    stale.version = 0
    stale.reprice(999, _rate("9"))
    with pytest.raises(SheetVersionConflict) as caught:
        repository.save(stale)
    assert str(caught.value) == (
        f"save: версия листа разошлась, id={sheet_id}"
    )
    seen = repository.take(sheet_id)
    assert seen.density == 180
    assert seen.cost == _rate("2")
    assert seen.version == 1
    assert seen.format.name == "450 x 320"
    assert seen.format.height == 450
    assert seen.format.width == 320


def test_should_remove_a_free_sheet_from_the_catalog(
    catalog: tuple[SqlSheetRepository, list[int]],
) -> None:
    repository, saved = catalog
    assert list(inspect.signature(SqlSheetRepository.delete).parameters) == [
        "self",
        "sheet_id",
    ]
    sheet_id = _new_sheet(repository, saved)
    repository.delete(sheet_id)
    assert all(item.id != sheet_id for item in repository.take_all())


def test_should_keep_the_sheet_and_the_printing_when_the_sheet_is_in_use(
    catalog: tuple[SqlSheetRepository, list[int]],
    engine: Engine,
) -> None:
    repository, saved = catalog
    sheet_id = _new_sheet(repository, saved)
    orders = SqlWorkplaceOrderRepository(engine)
    order_id = orders.save(_linked_order(sheet_id))
    try:
        with pytest.raises(SheetInUse) as caught:
            repository.delete(sheet_id)
        assert str(caught.value) == f"delete: лист занят, id={sheet_id}"
        assert repository.take(sheet_id).id == sheet_id
        taken = orders.take(order_id)
        assert taken.printings[0].specification.press_sheet == sheet_id
        assert taken.printings[0].specification.spacing == 4
    finally:
        orders.delete(order_id)


def test_should_keep_the_sheet_when_the_reference_uses_it(
    catalog: tuple[SqlSheetRepository, list[int]],
    engine: Engine,
) -> None:
    repository, saved = catalog
    sheet_id = _new_sheet(repository, saved)
    orders = SqlWorkplaceOrderRepository(engine)
    previous = _reference_document(engine)
    try:
        orders.set_reference(_linked_order(sheet_id))
        with pytest.raises(SheetInUse) as caught:
            repository.delete(sheet_id)
        assert str(caught.value) == f"delete: лист занят, id={sheet_id}"
        assert repository.take(sheet_id).id == sheet_id
        taken = orders.reference()
        assert taken is not None
        assert taken.printings[0].specification.press_sheet == sheet_id
        assert taken.printings[0].specification.spacing == 4
    finally:
        _restore_reference(engine, previous)


def test_should_report_sheet_not_found_for_an_unknown_id(
    catalog: tuple[SqlSheetRepository, list[int]],
) -> None:
    repository, _saved = catalog
    with pytest.raises(SheetNotFound) as caught:
        repository.delete(_MISSING_ID)
    assert str(caught.value) == f"delete: листа нет, id={_MISSING_ID}"
