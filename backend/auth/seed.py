"""Admin user seed on empty database."""

from __future__ import annotations

from backend.auth.errors import AdminSeedConfigError
from backend.auth.passwords import hash_password
from backend.auth.users import UserStore


def seed_admin_if_empty(
    store: UserStore,
    username: str | None,
    password: str | None,
) -> None:
    """Creates the first admin user when the store is empty.

    :param store:
    :param username: ``ADMIN_USERNAME`` value.
    :param password: ``ADMIN_PASSWORD`` value.

    :raises AdminSeedConfigError: when the store is empty and env is incomplete.

    :return: nothing.
    """
    if store.count() > 0:
        return
    if not username or not password:
        raise AdminSeedConfigError(
            "ADMIN_USERNAME and ADMIN_PASSWORD are required when users table is empty",
        )
    store.add(username, hash_password(password))
