import pytest

from backend.auth.errors import AdminSeedConfigError
from backend.auth.seed import seed_admin_if_empty


class _MemStore:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str]] = []

    def count(self) -> int:
        return len(self.rows)

    def get_by_username(self, username: str):
        return None

    def add(self, username: str, password_hash: str) -> None:
        self.rows.append((username, password_hash))


def test_seed_inserts_once():
    store = _MemStore()
    seed_admin_if_empty(store, "admin", "pass")
    assert len(store.rows) == 1
    assert store.rows[0][0] == "admin"


def test_seed_noop_when_rows_exist():
    store = _MemStore()
    store.rows.append(("x", "h"))
    seed_admin_if_empty(store, "admin", "pass")
    assert store.rows == [("x", "h")]


def test_seed_raises_when_empty_and_env_missing():
    store = _MemStore()
    with pytest.raises(AdminSeedConfigError):
        seed_admin_if_empty(store, None, None)
