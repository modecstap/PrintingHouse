"""Equipment catalog routes with a fake :class:`EquipmentCatalogService`."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

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
    missing_printer_ids: set[int] = field(default_factory=set)
    calls: list[str] = field(default_factory=list)
    last_replace_printer: Printer | None = None

    def printers(self) -> tuple[Printer, ...]:
        self.calls.append("list")
        return self.printers_rows

    def printer(self, printer_id: PrinterID) -> Printer:
        self.calls.append(f"get:{printer_id.value}")
        return self.printers_rows[0]

    def save_printer(self, printer: Printer) -> None:
        self.calls.append(f"save:{printer.id.value}")

    def create_printer(
        self,
        name: str,
        spacing: int,
        startup: Money,
        cyan: Money,
        magenta: Money,
        yellow: Money,
        black: Money,
    ) -> PrinterID:
        self.calls.append("create_printer")
        return PrinterID(7)

    def replace_printer(self, printer: Printer) -> None:
        if printer.id.value in self.missing_printer_ids:
            raise KeyError(printer.id)
        self.calls.append(f"replace:{printer.id.value}")
        self.last_replace_printer = printer

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


_PRINTER_WRITE_JSON = {
    "name": "Тест",
    "spacing": 0,
    "startup": "0",
    "cyan": "0",
    "magenta": "0",
    "yellow": "0",
    "black": "0",
}


def test_create_printer_returns_id():
    fake = _FakeEquipmentService()
    client, headers = _client_with_fake(fake)
    response = client.post(
        "/api/equipment/printers",
        headers=headers,
        json=_PRINTER_WRITE_JSON,
    )
    assert response.status_code == 200
    assert response.json() == {"id": 7}
    assert fake.calls == ["create_printer"]


_PRINTER_JSON = {
    "id": 5,
    "name": "Тест",
    "spacing": 0,
    "startup": "0",
    "cyan": "0",
    "magenta": "0",
    "yellow": "0",
    "black": "0",
}


def test_replace_printer_204():
    fake = _FakeEquipmentService()
    client, headers = _client_with_fake(fake)
    response = client.put(
        "/api/equipment/printers/5",
        headers=headers,
        json=_PRINTER_JSON,
    )
    assert response.status_code == 204
    assert fake.calls == ["replace:5"]
    assert fake.last_replace_printer == Printer(
        id=PrinterID(5),
        name="Тест",
        spacing=0,
        startup=Money(Decimal("0")),
        cyan=Money(Decimal("0")),
        magenta=Money(Decimal("0")),
        yellow=Money(Decimal("0")),
        black=Money(Decimal("0")),
    )


def test_replace_printer_400_when_body_id_differs():
    fake = _FakeEquipmentService()
    client, headers = _client_with_fake(fake)
    body = dict(_PRINTER_JSON, id=6)
    response = client.put(
        "/api/equipment/printers/5",
        headers=headers,
        json=body,
    )
    assert response.status_code == 400
    assert fake.calls == []


def test_replace_printer_404_when_missing():
    fake = _FakeEquipmentService(missing_printer_ids={9})
    client, headers = _client_with_fake(fake)
    body = dict(_PRINTER_JSON, id=9)
    response = client.put(
        "/api/equipment/printers/9",
        headers=headers,
        json=body,
    )
    assert response.status_code == 404


def test_replace_printer_requires_token():
    fake = _FakeEquipmentService()
    client, _ = _client_with_fake(fake)
    assert client.put("/api/equipment/printers/5", json=_PRINTER_JSON).status_code == 401
