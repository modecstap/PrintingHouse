"""Equipment catalog routes with a fake :class:`PrinterCatalog`."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.auth.config import AuthConfig
from backend.auth.passwords import hash_password
from backend.auth.tokens import create_access_token
from backend.new_core.equipment.printer import Printer, PrinterID, PrinterPrices
from backend.new_core.values.money import Money
from backend.server import dependencies
from backend.server.app import create_app
from backend.test.server.conftest import InMemoryUserStore, _DummyDatabase


__all__ = [
    "test_equipment_routes_require_token",
    "test_create_printer_returns_id",
    "test_replace_printer_204",
    "test_replace_printer_400_when_body_id_differs",
    "test_replace_printer_404_when_missing",
    "test_replace_printer_requires_token",
]

@dataclass
class _FakePrinterCatalog:
    """Fake Printer Catalog.
    """
    printers_rows: tuple[Printer, ...] = ()
    missing_printer_ids: set[int] = field(default_factory=set)
    calls: list[str] = field(default_factory=list)
    last_replace_printer: Printer | None = None

    def printers(self) -> tuple[Printer, ...]:
        """Handles printers.

        :return: the tuple[Printer, ...] result.
        """
        self.calls.append("list")
        return self.printers_rows

    def printer(self, printer_id: PrinterID) -> Printer:
        """Handles printer.

        :param printer_id: id of the printer.

        :return: the Printer result.
        """
        self.calls.append(f"get:{printer_id.value}")
        return self.printers_rows[0]

    def save_printer(self, printer: Printer) -> None:
        """Persists the printer.

        :param printer: the printer.
        """
        self.calls.append(f"save:{printer.id.value}")

    def create_printer(
        self,
        name: str,
        prices,
    ) -> PrinterID:
        """Creates a printer.

        :param name: the name.
        :param prices: the prices.

        :return: the PrinterID result.
        """
        self.calls.append("create_printer")
        return PrinterID(7)

    def replace_printer(self, printer: Printer) -> None:
        """Replaces the printer.

        :param printer: the printer.

        :raises KeyError: when the operation fails.
        """
        if printer.id.value in self.missing_printer_ids:
            raise KeyError(printer.id)
        self.calls.append(f"replace:{printer.id.value}")
        self.last_replace_printer = printer

    def delete_printer(self, printer_id: PrinterID) -> None:
        """Deletes the printer.

        :param printer_id: id of the printer.
        """
        self.calls.append(f"delete:{printer_id.value}")


_AUTH = AuthConfig("unit-test-secret", "HS256", 60)


def _client_with_fake(
        fake: _FakePrinterCatalog) -> tuple[TestClient, dict[str, str]]:
    """Handles client with fake.

    :param fake: the fake.

    :return: the tuple[TestClient, dict[str, str]] result.
    """
    store = InMemoryUserStore({"tester": hash_password("pass")})
    app = create_app(_AUTH, _DummyDatabase())
    app.dependency_overrides[dependencies.get_printer_catalog] = lambda: fake
    app.dependency_overrides[dependencies.get_user_store] = lambda: store
    app.dependency_overrides[dependencies.get_auth_config] = lambda: _AUTH
    token = create_access_token("tester", _AUTH)
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app), headers


def test_equipment_routes_require_token():
    """Handles test equipment routes require token.
    """
    fake = _FakePrinterCatalog()
    client, _ = _client_with_fake(fake)
    assert client.get("/api/equipment/printers").status_code == 401


_PRINTER_WRITE_JSON = {
    "name": "Тест",
    "startup": "0",
    "cyan": "0",
    "magenta": "0",
    "yellow": "0",
    "black": "0",
}


def test_create_printer_returns_id():
    """Handles test create printer returns id.
    """
    fake = _FakePrinterCatalog()
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
    "startup": "0",
    "cyan": "0",
    "magenta": "0",
    "yellow": "0",
    "black": "0",
}


def test_replace_printer_204():
    """Handles test replace printer 204.
    """
    fake = _FakePrinterCatalog()
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
        prices=PrinterPrices(
            startup=Money(Decimal("0")),
            cyan=Money(Decimal("0")),
            magenta=Money(Decimal("0")),
            yellow=Money(Decimal("0")),
            black=Money(Decimal("0")),
        ),
    )


def test_replace_printer_400_when_body_id_differs():
    """Handles test replace printer 400 when body id differs.
    """
    fake = _FakePrinterCatalog()
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
    """Handles test replace printer 404 when missing.
    """
    fake = _FakePrinterCatalog(missing_printer_ids={9})
    client, headers = _client_with_fake(fake)
    body = dict(_PRINTER_JSON, id=9)
    response = client.put(
        "/api/equipment/printers/9",
        headers=headers,
        json=body,
    )
    assert response.status_code == 404


def test_replace_printer_requires_token():
    """Handles test replace printer requires token.
    """
    fake = _FakePrinterCatalog()
    client, _ = _client_with_fake(fake)
    assert client.put(
        "/api/equipment/printers/5",
        json=_PRINTER_JSON).status_code == 401
