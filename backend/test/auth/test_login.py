"""Tests for auth.test_login.py.
"""

import pytest

from backend.auth.config import AuthConfig
from backend.auth.errors import InvalidCredentials
from backend.auth.login import PasswordLogin, login
from backend.auth.passwords import hash_password


__all__ = [
    "test_login_ok",
    "test_login_bad_password",
]

class _FakeStore:
    """Fake Store.
    """
    def __init__(self, user: tuple[str, str] | None):
        """Initializes this instance.

        :param user: the user.
        """
        self._user = user

    def count(self) -> int:
        """Handles count.

        :return: the int result.
        """
        return 1 if self._user else 0

    def get_by_username(self, username: str):
        """Returns the by username.

        :param username: the username.

        :return: the computed value.
        """
        from backend.auth.users import StoredUser

        if self._user and self._user[0] == username:
            return StoredUser(username=username, password_hash=self._user[1])
        return None

    def add(self, username: str, password_hash: str) -> None:
        """Adds a add.

        :param username: the username.
        :param password_hash: the password hash.

        :raises AssertionError: when the operation fails.
        """
        raise AssertionError("not used")


def test_login_ok():
    """Handles test login ok.
    """
    cfg = AuthConfig("k", "HS256", 10)
    store = _FakeStore(("u", hash_password("p")))
    token = login(PasswordLogin("u", "p"), store, cfg)
    assert isinstance(token, str) and token


def test_login_bad_password():
    """Handles test login bad password.
    """
    cfg = AuthConfig("k", "HS256", 10)
    store = _FakeStore(("u", hash_password("p")))
    with pytest.raises(InvalidCredentials):
        login(PasswordLogin("u", "wrong"), store, cfg)
