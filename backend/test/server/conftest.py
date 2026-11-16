"""Shared TestClient fixtures for HTTP tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.auth.config import AuthConfig
from backend.auth.passwords import hash_password
from backend.auth.tokens import create_access_token
from backend.auth.users import StoredUser
from backend.server.app import create_app


__all__ = [
    "InMemoryUserStore",
    "auth_config",
    "user_store",
    "api_client",
    "bearer_token",
    "auth_headers",
]

class _DummySession:
    """Dummy Session.
    """
    def close(self) -> None:
        """Handles close.
        """
        return None

    def commit(self) -> None:
        """Handles commit.
        """
        return None


class _DummyDatabase:
    """Dummy Database.
    """
    def __init__(self) -> None:
        """Initializes this instance.
        """
        self.session_factory = lambda: _DummySession()


class InMemoryUserStore:
    """In Memory User Store.
    """
    def __init__(self, users: dict[str, str] | None = None) -> None:
        """Initializes this instance.

        :param users: the users.
        """
        self._users = users or {}

    def count(self) -> int:
        """Handles count.

        :return: the int result.
        """
        return len(self._users)

    def get_by_username(self, username: str) -> StoredUser | None:
        """Returns the by username.

        :param username: the username.

        :return: the StoredUser | None result.
        """
        stored = self._users.get(username)
        if stored is None:
            return None
        return StoredUser(username=username, password_hash=stored)

    def add(self, username: str, password_hash: str) -> None:
        """Adds a add.

        :param username: the username.
        :param password_hash: the password hash.
        """
        self._users[username] = password_hash


@pytest.fixture
def auth_config() -> AuthConfig:
    """Handles auth config.

    :return: the AuthConfig result.
    """
    return AuthConfig(
        secret_key="unit-test-secret",
        algorithm="HS256",
        access_token_expire_minutes=60,
    )


@pytest.fixture
def user_store() -> InMemoryUserStore:
    """Handles user store.

    :return: the InMemoryUserStore result.
    """
    return InMemoryUserStore({"tester": hash_password("pass")})


@pytest.fixture
def api_client(auth_config, user_store):
    """Handles api client.

    :param auth_config: the auth config.
    :param user_store: the user store.
    """
    app = create_app(auth_config, _DummyDatabase())

    from backend.server import dependencies

    app.dependency_overrides[dependencies.get_user_store] = lambda: user_store
    app.dependency_overrides[dependencies.get_auth_config] = lambda: auth_config

    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def bearer_token(auth_config) -> str:
    """Handles bearer token.

    :param auth_config: the auth config.

    :return: the str result.
    """
    return create_access_token("tester", auth_config)


@pytest.fixture
def auth_headers(bearer_token) -> dict[str, str]:
    """Handles auth headers.

    :param bearer_token: the bearer token.

    :return: the dict[str, str] result.
    """
    return {"Authorization": f"Bearer {bearer_token}"}
