"""Edges catalog routes with a fake catalog."""

from __future__ import annotations

from dataclasses import dataclass, field

from fastapi.testclient import TestClient

from backend.auth.config import AuthConfig
from backend.auth.passwords import hash_password
from backend.auth.tokens import create_access_token
from backend.new_core.edges import Edges, EdgesID
from backend.server import dependencies
from backend.server.app import create_app
from backend.test.server.conftest import InMemoryUserStore, _DummyDatabase

__all__ = [
    "test_edges_require_token",
    "test_create_edges_200_returns_assigned_id",
]

_AUTH = AuthConfig("unit-test-secret", "HS256", 60)


@dataclass
class _FakeEdgesCatalog:
    """Fake Edges Catalog.
    """
    calls: list[str] = field(default_factory=list)
    created_edges_id: int = 3
    last_create: tuple[str, int, int] | None = None

    def edges_rows(self) -> tuple[Edges, ...]:
        self.calls.append("list")
        return ()

    def edges_row(self, edges_id: EdgesID) -> Edges:
        self.calls.append(f"get:{edges_id.value}")
        return Edges(id=edges_id, name="", bleeds=0, spacing=0)

    def create_edges(self, name: str, bleeds: int, spacing: int) -> EdgesID:
        self.calls.append("create")
        self.last_create = (name, bleeds, spacing)
        return EdgesID(self.created_edges_id)

    def replace_edges(self, edges: Edges) -> None:
        self.calls.append(f"replace:{edges.id.value}")

    def delete_edges(self, edges_id: EdgesID) -> None:
        self.calls.append(f"delete:{edges_id.value}")


def _client_with_fake(
    fake: _FakeEdgesCatalog | None = None,
) -> tuple[TestClient, dict[str, str]]:
    """Handles client with fake edges catalog.

    :param fake: the fake catalog.

    :return: the tuple[TestClient, dict[str, str]] result.
    """
    catalog = fake if fake is not None else _FakeEdgesCatalog()
    store = InMemoryUserStore({"tester": hash_password("pass")})
    app = create_app(_AUTH, _DummyDatabase())
    app.dependency_overrides[dependencies.get_edges_catalog] = lambda: catalog
    app.dependency_overrides[dependencies.get_edges_catalog_and_session] = (
        lambda: (catalog, _DummyDatabase().session())
    )
    app.dependency_overrides[dependencies.get_user_store] = lambda: store
    app.dependency_overrides[dependencies.get_auth_config] = lambda: _AUTH
    token = create_access_token("tester", _AUTH)
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app), headers


def test_edges_require_token() -> None:
    """GET /api/edges without a token returns 401."""
    client, _ = _client_with_fake()
    assert client.get("/api/edges").status_code == 401


def test_create_edges_200_returns_assigned_id() -> None:
    """POST /api/edges returns the id from the catalog service."""
    fake = _FakeEdgesCatalog(created_edges_id=9)
    client, headers = _client_with_fake(fake)
    response = client.post(
        "/api/edges",
        headers=headers,
        json={"name": "std", "bleeds": 2, "spacing": 5},
    )
    assert response.status_code == 200
    assert response.json() == {"id": 9}
    assert fake.last_create == ("std", 2, 5)