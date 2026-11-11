"""Reference repository append semantics."""

from backend.new_core.order.order import OrderID
from backend.new_core.reference.reference import Reference
from backend.storage.order.repository import SqlOrderRepository
from backend.storage.reference.repository import SqlReferenceRepository
from backend.test.new_core.test_print_run import build_worked_run
from backend.test.storage.catalog_insert import insert_catalogs_from_ctx
from backend.test.storage.helpers import make_order, product_from_run
from backend.new_core import Order


def test_save_appends_references_in_insertion_order(db_session):
    """``take_all`` returns rows in store order without rewriting earlier ones."""
    run, *_ , ctx = build_worked_run()
    insert_catalogs_from_ctx(db_session, ctx)
    orders = SqlOrderRepository(db_session)
    refs = SqlReferenceRepository(db_session)
    order = make_order(6, product_from_run(run), 1)

    with db_session.begin():
        orders.save(order)
        refs.save(Reference(name="first", description="a", order_id=order.id))
        refs.save(Reference(name="second", description="b", order_id=order.id))

    loaded = refs.take_all()
    assert [(row.name, row.description) for row in loaded] == [
        ("first", "a"),
        ("second", "b"),
    ]
