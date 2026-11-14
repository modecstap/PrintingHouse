"""Staff catalog routes with a fake :class:`StaffCatalogService`."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.auth.config import AuthConfig
from backend.auth.passwords import hash_password
from backend.auth.tokens import create_access_token
from backend.new_core.personal.press_operator import PressOperator, PressOperatorID
from backend.new_core.values.money import Money
from backend.server import dependencies
from backend.server.app import create_app
from backend.test.server.conftest import InMemoryUserStore, _DummyDatabase


@dataclass
class _FakeStaffCatalogService:
    missing_press_operator_ids: set[int] = field(default_factory=set)
    calls: list[str] = field(default_factory=list)
    last_replace_press_operator: PressOperator | None = None

    def press_operators(self) -> tuple:
        return ()

    def press_operator(self, operator_id: PressOperatorID) -> PressOperator:
        raise KeyError(operator_id)

    def save_press_operator(self, operator: PressOperator) -> None:
        pass

    def replace_press_operator(self, operator: PressOperator) -> None:
        if operator.id.value in self.missing_press_operator_ids:
            raise KeyError(operator.id)
        self.calls.append(f"replace:{operator.id.value}")
        self.last_replace_press_operator = operator

    def delete_press_operator(self, operator_id: PressOperatorID) -> None:
        pass

    def laminator_operators(self) -> tuple:
        return ()

    def laminator_operator(self, operator_id):
        raise KeyError(operator_id)

    def save_laminator_operator(self, operator) -> None:
        pass

    def delete_laminator_operator(self, operator_id) -> None:
        pass

    def cutter_operators(self) -> tuple:
        return ()

    def cutter_operator(self, operator_id):
        raise KeyError(operator_id)

    def save_cutter_operator(self, operator) -> None:
        pass

    def delete_cutter_operator(self, operator_id) -> None:
        pass

    def die_cut_operators(self) -> tuple:
        return ()

    def die_cut_operator(self, operator_id):
        raise KeyError(operator_id)

    def save_die_cut_operator(self, operator) -> None:
        pass

    def delete_die_cut_operator(self, operator_id) -> None:
        pass


_AUTH = AuthConfig("unit-test-secret", "HS256", 60)


def _client_with_fake(
    fake: _FakeStaffCatalogService,
) -> tuple[TestClient, dict[str, str]]:
    store = InMemoryUserStore({"tester": hash_password("pass")})
    app = create_app(_AUTH, _DummyDatabase())
    app.dependency_overrides[dependencies.get_staff_catalog_service] = lambda: fake
    app.dependency_overrides[dependencies.get_user_store] = lambda: store
    app.dependency_overrides[dependencies.get_auth_config] = lambda: _AUTH
    token = create_access_token("tester", _AUTH)
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app), headers


_OPERATOR_JSON = {"id": 5, "name": "Оператор", "salary_by_operation": "100.50"}


def test_staff_routes_require_token():
    fake = _FakeStaffCatalogService()
    client, _ = _client_with_fake(fake)
    assert client.get("/api/staff/press-operators").status_code == 401


def test_replace_press_operator_204():
    fake = _FakeStaffCatalogService()
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
    fake = _FakeStaffCatalogService(missing_press_operator_ids={9})
    client, headers = _client_with_fake(fake)
    body = dict(_OPERATOR_JSON, id=9)
    response = client.put(
        "/api/staff/press-operators/9",
        headers=headers,
        json=body,
    )
    assert response.status_code == 404