"""Reference routes with a fake :class:`ReferenceOrderService`."""

from __future__ import annotations

from dataclasses import dataclass, field

from fastapi.testclient import TestClient

from backend.auth.config import AuthConfig
from backend.auth.passwords import hash_password
from backend.auth.tokens import create_access_token
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.repository import OrderNotFound
from backend.new_core.reference.reference import Reference
from backend.server import dependencies
from backend.server.app import create_app
from backend.test.new_core.test_print_run import build_worked_run
from backend.test.server.conftest import InMemoryUserStore, _DummyDatabase
from backend.test.storage.helpers import make_order, product_from_run


@dataclass
class _FakeReferenceService:
    references_rows: tuple[Reference, ...] = ()
    orders_rows: tuple[Order, ...] = ()
    save_error: Exception | None = None
    calls: list[str] = field(default_factory=list)

    def references(self) -> tuple[Reference, ...]:
        self.calls.append("list")
        return self.references_rows

    def reference_orders(self) -> tuple[Order, ...]:
        self.calls.append("orders")
        return self.orders_rows

    def save(self, reference: Reference) -> None:
        self.calls.append(f"save:{reference.name}")
        if self.save_error:
            raise self.save_error


_AUTH = AuthConfig("unit-test-secret", "HS256", 60)


def _client_with_fake(fake: _FakeReferenceService) -> tuple[TestClient, dict[str, str]]:
    store = InMemoryUserStore({"tester": hash_password("pass")})
    app = create_app(_AUTH, _DummyDatabase())
    app.dependency_overrides[dependencies.get_reference_service] = lambda: fake
    app.dependency_overrides[dependencies.get_user_store] = lambda: store
    app.dependency_overrides[dependencies.get_auth_config] = lambda: _AUTH
    token = create_access_token("tester", _AUTH)
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app), headers


def test_references_without_token_401():
    fake = _FakeReferenceService()
    client, _ = _client_with_fake(fake)
    assert client.get("/api/references").status_code == 401


def test_list_and_orders_happy_path():
    run, *_ = build_worked_run()
    product = product_from_run(run)
    order = make_order(1, product, 1)
    ref = Reference(name="r1", description="d", order_id=order.id)
    fake = _FakeReferenceService(references_rows=(ref,), orders_rows=(order,))
    client, headers = _client_with_fake(fake)
    assert client.get("/api/references", headers=headers).json() == [
        {"name": "r1", "description": "d", "order_id": 1},
    ]
    orders = client.get("/api/references/orders", headers=headers).json()
    assert len(orders) == 1
    assert orders[0]["id"] == 1


def test_save_204_without_body():
    fake = _FakeReferenceService()
    client, headers = _client_with_fake(fake)
    response = client.post(
        "/api/references",
        headers=headers,
        json={"name": "n", "description": "d", "order_id": 2},
    )
    assert response.status_code == 204
    assert response.content == b""
    assert fake.calls == ["save:n"]


def test_save_404_when_order_missing():
    fake = _FakeReferenceService(
        save_error=OrderNotFound("take", OrderID(2)),
    )
    client, headers = _client_with_fake(fake)
    response = client.post(
        "/api/references",
        headers=headers,
        json={"name": "n", "description": "d", "order_id": 2},
    )
    assert response.status_code == 404
