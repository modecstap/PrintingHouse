"""Password login."""

from __future__ import annotations

from dataclasses import dataclass

from backend.auth.config import AuthConfig
from backend.auth.errors import InvalidCredentials
from backend.auth.passwords import verify_password
from backend.auth.tokens import create_access_token
from backend.auth.users import UserStore


@dataclass(frozen=True)
class PasswordLogin:  # pylint: disable=too-few-public-methods
    """Username and password for authentication."""

    username: str
    password: str


def login(
    credentials: PasswordLogin,
    store: UserStore,
    config: AuthConfig,
) -> str:
    """Authenticates and returns an access token.

    :param credentials:
    :param store:
    :param config:

    :raises InvalidCredentials: on unknown user or bad password.

    :return: JWT access token.
    """
    user = store.get_by_username(credentials.username)
    if user is None or not verify_password(
        credentials.password,
        user.password_hash,
    ):
        raise InvalidCredentials("Incorrect username or password")
    return create_access_token(user.username, config)