"""Equipment catalog routes with a fake :class:`EquipmentCatalogService`."""

from __future__ import annotations

from dataclasses import dataclass, field

from fastapi.testclient import TestClient

from backend.auth.config import AuthConfig
from backend.auth.passwords import hash_password
from backend.auth.tokens import create_access_token
from backend.new_core.equipment.printer import Printer, PrinterID
from backend.new_core.values.money import Money
from backend.server import dependencies
from backend.server.app import create_app
from backend.test.server.conftest import InMemoryUserStore, _DummyDatabase


@dataclass
class _FakeEquipmentService:
    printers_rows: tuple[Printer, ...] = ()
    calls: list[str] = field(default_factory=list)

    def printers(self) -> tuple[Printer, ...]:
        self.calls.append("list")
        return self.printers_rows

    def printer(self, printer_id: PrinterID) -> Printer:
        self.calls.append(f"get:{printer_id.value}")
        return self.printers_rows[0]

    def save_printer(self, printer: Printer) -> None:
        self.calls.append(f"save:{printer.id.value}")

    def delete_printer(self, printer_id: PrinterID) -> None:
        self.calls.append(f"delete:{printer_id.value}")

    def laminators(self) -> tuple:
        return ()

    def laminator(self, laminator_id):
        raise KeyError(laminator_id)

    def save_laminator(self, laminator) -> None:
        pass

    def delete_laminator(self, laminator_id) -> None:
        pass

    def cutters(self) -> tuple:
        return ()

    def cutter(self, cutter_id):
        raise KeyError(cutter_id)

    def save_cutter(self, cutter) -> None:
        pass

    def delete_cutter(self, cutter_id) -> None:
        pass


_AUTH = AuthConfig("unit-test-secret", "HS256", 60)


def _client_with_fake(fake: _FakeEquipmentService) -> tuple[TestClient, dict[str, str]]:
    store = InMemoryUserStore({"tester": hash_password("pass")})
    app = create_app(_AUTH, _DummyDatabase())
    app.dependency_overrides[dependencies.get_equipment_catalog_service] = lambda: fake
    app.dependency_overrides[dependencies.get_user_store] = lambda: store
    app.dependency_overrides[dependencies.get_auth_config] = lambda: _AUTH
    token = create_access_token("tester", _AUTH)
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app), headers


def test_equipment_routes_require_token():
    fake = _FakeEquipmentService()
    client, _ = _client_with_fake(fake)
    assert client.get("/api/equipment/printers").status_code == 401


def test_save_printer_204():
    fake = _FakeEquipmentService()
    client, headers = _client_with_fake(fake)
    response = client.post(
        "/api/equipment/printers",
        headers=headers,
        json={
            "id": 1,
            "startup": "0",
            "cyan": "0",
            "magenta": "0",
            "yellow": "0",
            "black": "0",
        },
    )
    assert response.status_code == 204
    assert fake.calls == ["save:1"]
