"""Order routes with a fake :class:`OrderService`."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.auth.config import AuthConfig
from backend.auth.passwords import hash_password
from backend.auth.tokens import create_access_token
from backend.new_core.accountant.order_report import OrderReport
from backend.new_core.application_services.order import OrderIdAllocationFailed
from backend.new_core.order.order import Order, OrderID
from backend.new_core.order.repository import OrderNotFound
from backend.new_core.values.money import Money
from backend.server import dependencies
from backend.server.app import create_app
from backend.test.new_core.test_print_run import build_worked_run
from backend.test.server.conftest import InMemoryUserStore, _DummyDatabase
from backend.test.storage.helpers import make_order, product_from_run


@dataclass
class _FakeOrderService:
    calls: list[str] = field(default_factory=list)
    quote_report: OrderReport | None = None
    save_id: OrderID = OrderID(9)
    orders: tuple[Order, ...] = ()
    quote_error: Exception | None = None
    save_error: Exception | None = None
    replace_error: Exception | None = None
    get_error: Exception | None = None

    def get_orders(self, limit: int) -> tuple[Order, ...]:
        self.calls.append(f"list:{limit}")
        return self.orders[:limit]

    def get_order(self, order_id: OrderID) -> Order:
        self.calls.append(f"get:{order_id.value}")
        if self.get_error:
            raise self.get_error
        for order in self.orders:
            if order.id == order_id:
                return order
        raise OrderNotFound("take", order_id)

    def order_report(self, order_id: OrderID) -> OrderReport:
        self.calls.append(f"report:{order_id.value}")
        return self.quote_report or OrderReport(
            product_price=Money(Decimal("1")),
            order_price=Money(Decimal("2")),
            income=Money(Decimal("1")),
            impositions=(1,),
        )

    def quote(self, product, count: int) -> OrderReport:
        self.calls.append(f"quote:{count}")
        if self.quote_error:
            raise self.quote_error
        return self.quote_report or OrderReport(
            product_price=Money(Decimal("3")),
            order_price=Money(Decimal("4")),
            income=Money(Decimal("1")),
            impositions=(2,),
        )

    def save(self, product, count: int, description: str = "") -> OrderID:
        self.calls.append(f"save:{count}:{description}")
        if self.save_error:
            raise self.save_error
        return self.save_id

    def replace(
        self,
        order_id: OrderID,
        product,
        count: int,
        description: str = "",
    ) -> OrderID:
        self.calls.append(f"replace:{order_id.value}:{count}:{description}")
        if self.replace_error:
            raise self.replace_error
        return order_id


_AUTH = AuthConfig("unit-test-secret", "HS256", 60)


def _client_with_fake(fake: _FakeOrderService) -> tuple[TestClient, dict[str, str]]:
    store = InMemoryUserStore({"tester": hash_password("pass")})
    app = create_app(_AUTH, _DummyDatabase())
    app.dependency_overrides[dependencies.get_order_service] = lambda: fake
    app.dependency_overrides[dependencies.get_user_store] = lambda: store
    app.dependency_overrides[dependencies.get_auth_config] = lambda: _AUTH
    token = create_access_token("tester", _AUTH)
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app), headers


def _product_payload() -> dict:
    run, *_ = build_worked_run()
    product = product_from_run(run)
    from backend.server.mapping import product_to_dto

    return {
        "product": product_to_dto(product).model_dump(),
        "count": 2,
    }


def test_orders_missing_token_401():
    fake = _FakeOrderService()
    client, _ = _client_with_fake(fake)
    response = client.get("/api/orders")
    assert response.status_code == 401


def test_quote_200_and_save_not_called():
    fake = _FakeOrderService()
    client, headers = _client_with_fake(fake)
    response = client.post("/api/orders/quote", headers=headers, json=_product_payload())
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"product_price", "order_price", "income", "impositions"}
    assert "save:" not in " ".join(fake.calls)


def test_save_returns_id():
    fake = _FakeOrderService(save_id=OrderID(42))
    client, headers = _client_with_fake(fake)
    response = client.post("/api/orders", headers=headers, json=_product_payload())
    assert response.status_code == 200
    assert response.json() == {"id": 42}


def test_save_passes_description_to_service():
    fake = _FakeOrderService()
    client, headers = _client_with_fake(fake)
    payload = _product_payload()
    payload["description"] = "листовка"
    client.post("/api/orders", headers=headers, json=payload)
    assert fake.calls == ["save:2:листовка"]


def test_get_order_404():
    fake = _FakeOrderService(get_error=OrderNotFound("take", OrderID(1)))
    client, headers = _client_with_fake(fake)
    response = client.get("/api/orders/1", headers=headers)
    assert response.status_code == 404


def test_list_limit_query():
    run, *_ = build_worked_run()
    order = make_order(1, product_from_run(run), 1)
    fake = _FakeOrderService(orders=(order,))
    client, headers = _client_with_fake(fake)
    response = client.get("/api/orders?limit=1", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert fake.calls == ["list:1"]


def test_bad_product_422():
    fake = _FakeOrderService()
    client, headers = _client_with_fake(fake)
    payload = _product_payload()
    payload["product"]["blocks"] = []
    response = client.post("/api/orders/quote", headers=headers, json=payload)
    assert response.status_code == 422


def test_save_409_on_allocation_failure():
    fake = _FakeOrderService(save_error=OrderIdAllocationFailed(OrderID(3)))
    client, headers = _client_with_fake(fake)
    response = client.post("/api/orders", headers=headers, json=_product_payload())
    assert response.status_code == 409


def test_quote_404_on_key_error():
    fake = _FakeOrderService(quote_error=KeyError("missing printer"))
    client, headers = _client_with_fake(fake)
    response = client.post("/api/orders/quote", headers=headers, json=_product_payload())
    assert response.status_code == 404


def test_replace_returns_same_id():
    fake = _FakeOrderService()
    client, headers = _client_with_fake(fake)
    payload = _product_payload()
    payload["count"] = 5
    response = client.put("/api/orders/17", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json() == {"id": 17}
    assert fake.calls == ["replace:17:5:"]


def test_replace_404_when_missing():
    fake = _FakeOrderService(
        replace_error=OrderNotFound("replace", OrderID(8)),
    )
    client, headers = _client_with_fake(fake)
    response = client.put("/api/orders/8", headers=headers, json=_product_payload())
    assert response.status_code == 404
