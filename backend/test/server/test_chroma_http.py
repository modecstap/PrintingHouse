"""Chroma catalog routes with a fake catalog."""

from __future__ import annotations

from dataclasses import dataclass, field

from fastapi.testclient import TestClient

from backend.auth.config import AuthConfig
from backend.auth.passwords import hash_password
from backend.auth.tokens import create_access_token
from backend.new_core.chroma import Chroma, ChromaID
from backend.new_core.values.percent import Percent
from backend.server import dependencies
from backend.server.app import create_app
from backend.test.server.conftest import InMemoryUserStore, _DummyDatabase

__all__ = [
    "test_chroma_require_token",
    "test_create_chroma_200_returns_assigned_id",
]

_AUTH = AuthConfig("unit-test-secret", "HS256", 60)


@dataclass
class _FakeChromaCatalog:
    """Fake Chroma Catalog.
    """
    calls: list[str] = field(default_factory=list)
    created_chroma_id: int = 3
    last_create: tuple[str, int, int, int, int] | None = None

    def chroma_rows(self) -> tuple[Chroma, ...]:
        self.calls.append("list")
        return ()

    def chroma_row(self, chroma_id: ChromaID) -> Chroma:
        self.calls.append(f"get:{chroma_id.value}")
        return Chroma(
            id=chroma_id,
            name="",
            cyan=Percent(0),
            magenta=Percent(0),
            yellow=Percent(0),
            black=Percent(0),
        )

    def create_chroma(
        self,
        name: str,
        cyan: int,
        magenta: int,
        yellow: int,
        black: int,
    ) -> ChromaID:
        self.calls.append("create")
        self.last_create = (name, cyan, magenta, yellow, black)
        return ChromaID(self.created_chroma_id)

    def replace_chroma(self, chroma: Chroma) -> None:
        self.calls.append(f"replace:{chroma.id.value}")

    def delete_chroma(self, chroma_id: ChromaID) -> None:
        self.calls.append(f"delete:{chroma_id.value}")


def _client_with_fake(
    fake: _FakeChromaCatalog | None = None,
) -> tuple[TestClient, dict[str, str]]:
    """Handles client with fake chroma catalog.

    :param fake: the fake catalog.

    :return: the tuple[TestClient, dict[str, str]] result.
    """
    catalog = fake if fake is not None else _FakeChromaCatalog()
    store = InMemoryUserStore({"tester": hash_password("pass")})
    app = create_app(_AUTH, _DummyDatabase())
    app.dependency_overrides[dependencies.get_chroma_catalog] = lambda: catalog
    app.dependency_overrides[dependencies.get_chroma_catalog_and_session] = (
        lambda: (catalog, _DummyDatabase().session())
    )
    app.dependency_overrides[dependencies.get_user_store] = lambda: store
    app.dependency_overrides[dependencies.get_auth_config] = lambda: _AUTH
    token = create_access_token("tester", _AUTH)
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app), headers


def test_chroma_require_token() -> None:
    """GET /api/chroma without a token returns 401."""
    client, _ = _client_with_fake()
    assert client.get("/api/chroma").status_code == 401


def test_create_chroma_200_returns_assigned_id() -> None:
    """POST /api/chroma returns the id from the catalog service."""
    fake = _FakeChromaCatalog(created_chroma_id=9)
    client, headers = _client_with_fake(fake)
    response = client.post(
        "/api/chroma",
        headers=headers,
        json={
            "name": "4+0",
            "cyan": 100,
            "magenta": 100,
            "yellow": 100,
            "black": 100,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"id": 9}
    assert fake.last_create == ("4+0", 100, 100, 100, 100)