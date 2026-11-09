"""User store protocol for login and admin seed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class StoredUser:
    """Username and password hash loaded from persistence."""

    username: str
    password_hash: str


class UserStore(Protocol):
    """Minimal user persistence for auth."""

    def count(self) -> int:
        """Returns how many users exist."""

    def get_by_username(self, username: str) -> StoredUser | None:
        """Returns one user or ``None``."""

    def add(self, username: str, password_hash: str) -> None:
        """Persists a new user."""
