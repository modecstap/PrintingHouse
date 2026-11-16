"""User store protocol for login and admin seed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


__all__ = [
    "StoredUser",
    "UserStore",
]

@dataclass(frozen=True, slots=True)
class StoredUser:
    """Username and password hash loaded from persistence."""

    username: str
    password_hash: str


class UserStore(Protocol):
    """Minimal user persistence for auth."""

    def count(self) -> int:
        """Returns how many users exist.

        :return: the int result.
        """

    def get_by_username(self, username: str) -> StoredUser | None:
        """Returns one user or ``None``.

        :param username: the username.

        :return: the StoredUser | None result.
        """

    def add(self, username: str, password_hash: str) -> None:
        """Persists a new user.

        :param username: the username.
        :param password_hash: the password hash.
        """
