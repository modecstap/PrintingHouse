"""Tests for auth.test_seed.py.
"""

import pytest

from backend.auth.errors import AdminSeedConfigError
from backend.auth.seed import seed_admin_if_empty


__all__ = [
    "test_seed_inserts_once",
    "test_seed_noop_when_rows_exist",
    "test_seed_raises_when_empty_and_env_missing",
]

class _MemStore:
    """Mem Store.
    """
    def __init__(self) -> None:
        """Initializes this instance.
        """
        self.rows: list[tuple[str, str]] = []

    def count(self) -> int:
        """Handles count.

        :return: the int result.
        """
        return len(self.rows)

    def get_by_username(self, username: str):
        """Returns the by username.

        :param username: the username.

        :return: the computed value.
        """
        return None

    def add(self, username: str, password_hash: str) -> None:
        """Adds a add.

        :param username: the username.
        :param password_hash: the password hash.
        """
        self.rows.append((username, password_hash))


def test_seed_inserts_once():
    """Handles test seed inserts once.
    """
    store = _MemStore()
    seed_admin_if_empty(store, "admin", "pass")
    assert len(store.rows) == 1
    assert store.rows[0][0] == "admin"


def test_seed_noop_when_rows_exist():
    """Handles test seed noop when rows exist.
    """
    store = _MemStore()
    store.rows.append(("x", "h"))
    seed_admin_if_empty(store, "admin", "pass")
    assert store.rows == [("x", "h")]


def test_seed_raises_when_empty_and_env_missing():
    """Handles test seed raises when empty and env missing.
    """
    store = _MemStore()
    with pytest.raises(AdminSeedConfigError):
        seed_admin_if_empty(store, None, None)
