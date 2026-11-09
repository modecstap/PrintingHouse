import pytest

from backend.auth.config import AuthConfig
from backend.auth.errors import InvalidCredentials
from backend.auth.login import login
from backend.auth.passwords import hash_password


class _FakeStore:
    def __init__(self, user: tuple[str, str] | None):
        self._user = user

    def count(self) -> int:
        return 1 if self._user else 0

    def get_by_username(self, username: str):
        from backend.auth.users import StoredUser

        if self._user and self._user[0] == username:
            return StoredUser(username=username, password_hash=self._user[1])
        return None

    def add(self, username: str, password_hash: str) -> None:
        raise AssertionError("not used")


def test_login_ok():
    cfg = AuthConfig("k", "HS256", 10)
    store = _FakeStore(("u", hash_password("p")))
    token = login("u", "p", store, cfg)
    assert isinstance(token, str) and token


def test_login_bad_password():
    cfg = AuthConfig("k", "HS256", 10)
    store = _FakeStore(("u", hash_password("p")))
    with pytest.raises(InvalidCredentials):
        login("u", "wrong", store, cfg)
