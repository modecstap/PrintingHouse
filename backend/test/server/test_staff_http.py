"""Staff catalog routes with a fake :class:`PressOperatorCatalog`."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.auth.config import AuthConfig
from backend.auth.passwords import hash_password
from backend.auth.tokens import create_access_token
from backend.new_core.personal.press_operator import (
    PressOperator,
    PressOperatorID,
)
from backend.new_core.values.money import Money
from backend.server import dependencies
from backend.server.app import create_app
from backend.test.server.conftest import InMemoryUserStore, _DummyDatabase


@dataclass
class _FakePressOperatorCatalog:
    missing_press_operator_ids: set[int] = field(default_factory=set)
    calls: list[str] = field(default_factory=list)
    last_replace_press_operator: PressOperator | None = None

    def press_operators(self) -> tuple:
        return ()

    def press_operator(self, operator_id: PressOperatorID) -> PressOperator:
        raise KeyError(operator_id)

    def save_press_operator(self, operator: PressOperator) -> None:
        pass

    def create_press_operator(
        self,
        name: str,
        salary_by_operation: Money,
    ) -> PressOperatorID:
        self.calls.append("create_press_operator")
        return PressOperatorID(3)

    def replace_press_operator(self, operator: PressOperator) -> None:
        if operator.id.value in self.missing_press_operator_ids:
            raise KeyError(operator.id)
        self.calls.append(f"replace:{operator.id.value}")
        self.last_replace_press_operator = operator

    def delete_press_operator(self, operator_id: PressOperatorID) -> None:
        pass


_AUTH = AuthConfig("unit-test-secret", "HS256", 60)


def _client_with_fake(
    fake: _FakePressOperatorCatalog,
) -> tuple[TestClient, dict[str, str]]:
    store = InMemoryUserStore({"tester": hash_password("pass")})
    app = create_app(_AUTH, _DummyDatabase())
    app.dependency_overrides[dependencies.get_press_operator_catalog] = lambda: fake
    app.dependency_overrides[dependencies.get_user_store] = lambda: store
    app.dependency_overrides[dependencies.get_auth_config] = lambda: _AUTH
    token = create_access_token("tester", _AUTH)
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app), headers


_OPERATOR_JSON = {"id": 5, "name": "Оператор", "salary_by_operation": "100.50"}


_OPERATOR_WRITE_JSON = {"name": "Оператор", "salary_by_operation": "100.50"}


def test_staff_routes_require_token():
    fake = _FakePressOperatorCatalog()
    client, _ = _client_with_fake(fake)
    assert client.get("/api/staff/press-operators").status_code == 401


def test_create_press_operator_returns_id():
    fake = _FakePressOperatorCatalog()
    client, headers = _client_with_fake(fake)
    response = client.post(
        "/api/staff/press-operators",
        headers=headers,
        json=_OPERATOR_WRITE_JSON,
    )
    assert response.status_code == 200
    assert response.json() == {"id": 3}
    assert fake.calls == ["create_press_operator"]


def test_replace_press_operator_204():
    fake = _FakePressOperatorCatalog()
    client, headers = _client_with_fake(fake)
    response = client.put(
        "/api/staff/press-operators/5",
        headers=headers,
        json=_OPERATOR_JSON,
    )
    assert response.status_code == 204
    assert fake.calls == ["replace:5"]
    assert fake.last_replace_press_operator == PressOperator(
        id=PressOperatorID(5),
        name="Оператор",
        salary_by_operation=Money(Decimal("100.50")),
    )


def test_replace_press_operator_404_when_missing():
    fake = _FakePressOperatorCatalog(missing_press_operator_ids={9})
    client, headers = _client_with_fake(fake)
    body = dict(_OPERATOR_JSON, id=9)
    response = client.put(
        "/api/staff/press-operators/9",
        headers=headers,
        json=body,
    )
    assert response.status_code == 404
