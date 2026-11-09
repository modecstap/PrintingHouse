"""Public docs and expired JWT hardening."""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from backend.server.app import create_app
from backend.test.server.conftest import InMemoryUserStore, _DummyDatabase, auth_config


def test_docs_reachable_without_auth(auth_config):
    client = TestClient(create_app(auth_config, _DummyDatabase()))
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_expired_jwt_on_protected_route_401(auth_config):
    app = create_app(auth_config, _DummyDatabase())
    store = InMemoryUserStore()
    from backend.server import dependencies

    app.dependency_overrides[dependencies.get_user_store] = lambda: store
    client = TestClient(app)
    expired = datetime.now(UTC) - timedelta(minutes=5)
    token = jwt.encode(
        {"sub": "x", "exp": expired},
        auth_config.secret_key,
        algorithm=auth_config.algorithm,
    )
    response = client.get(
        "/api/orders",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
