"""Password login."""

from __future__ import annotations

from backend.auth.config import AuthConfig
from backend.auth.errors import InvalidCredentials
from backend.auth.passwords import verify_password
from backend.auth.tokens import create_access_token
from backend.auth.users import UserStore


def login(username: str, password: str, store: UserStore, config: AuthConfig) -> str:
    """Authenticates and returns an access token.

    :param username:
    :param password:
    :param store:
    :param config:

    :raises InvalidCredentials: on unknown user or bad password.

    :return: JWT access token.
    """
    user = store.get_by_username(username)
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentials("Incorrect username or password")
    return create_access_token(user.username, config)
