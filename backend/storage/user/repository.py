"""SQL persistence for login users."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.auth.users import StoredUser, UserStore
from backend.storage.user.tables import UserRow


class SqlUserRepository(UserStore):
    """Stores username and password hash only."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def count(self) -> int:
        """Returns the number of stored users.

        :return: row count in ``users``.
        """
        return self._session.scalar(select(func.count()).select_from(UserRow)) or 0

    def get_by_username(self, username: str) -> StoredUser | None:
        """Loads one user by username.

        :param username:

        :return: stored credentials, or ``None`` if missing.
        """
        row = self._session.execute(
            select(UserRow).where(UserRow.username == username),
        ).scalar_one_or_none()
        if row is None:
            return None
        return StoredUser(username=row.username, password_hash=row.password_hash)

    def add(self, username: str, password_hash: str) -> None:
        """Inserts a user row.

        :param username:
        :param password_hash:

        :return: nothing.
        """
        self._session.add(UserRow(username=username, password_hash=password_hash))
