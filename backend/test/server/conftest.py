"""Shared TestClient fixtures for HTTP tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.auth.config import AuthConfig
from backend.auth.passwords import hash_password
from backend.auth.tokens import create_access_token
from backend.auth.users import StoredUser
from backend.server.app import create_app


class _DummySession:
    def close(self) -> None:
        return None

    def commit(self) -> None:
        return None


class _DummyDatabase:
    def __init__(self) -> None:
        self.session_factory = lambda: _DummySession()


class InMemoryUserStore:
    def __init__(self, users: dict[str, str] | None = None) -> None:
        self._users = users or {}

    def count(self) -> int:
        return len(self._users)

    def get_by_username(self, username: str) -> StoredUser | None:
        stored = self._users.get(username)
        if stored is None:
            return None
        return StoredUser(username=username, password_hash=stored)

    def add(self, username: str, password_hash: str) -> None:
        self._users[username] = password_hash


@pytest.fixture
def auth_config() -> AuthConfig:
    return AuthConfig(
        secret_key="unit-test-secret",
        algorithm="HS256",
        access_token_expire_minutes=60,
    )


@pytest.fixture
def user_store() -> InMemoryUserStore:
    return InMemoryUserStore({"tester": hash_password("pass")})


@pytest.fixture
def api_client(auth_config, user_store):
    app = create_app(auth_config, _DummyDatabase())

    from backend.server import dependencies

    app.dependency_overrides[dependencies.get_user_store] = lambda: user_store
    app.dependency_overrides[dependencies.get_auth_config] = lambda: auth_config

    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def bearer_token(auth_config) -> str:
    return create_access_token("tester", auth_config)


@pytest.fixture
def auth_headers(bearer_token) -> dict[str, str]:
    return {"Authorization": f"Bearer {bearer_token}"}
