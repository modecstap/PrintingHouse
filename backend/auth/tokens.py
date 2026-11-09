"""JWT access tokens."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

from backend.auth.config import AuthConfig
from backend.auth.errors import CredentialsError


def create_access_token(username: str, config: AuthConfig) -> str:
    """Issues a signed access token for ``username``.

    :param username:
    :param config:

    :return: encoded JWT string.
    """
    expire = datetime.now(UTC) + timedelta(minutes=config.access_token_expire_minutes)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, config.secret_key, algorithm=config.algorithm)


def decode_access_token(token: str, config: AuthConfig) -> str:
    """Decodes and validates an access token.

    :param token:
    :param config:

    :raises CredentialsError: on signature, expiry, or payload problems.

    :return: username from ``sub``.
    """
    try:
        payload = jwt.decode(
            token,
            config.secret_key,
            algorithms=[config.algorithm],
            options={"require": ["sub", "exp"]},
        )
    except jwt.InvalidTokenError as exc:
        raise CredentialsError("invalid token") from exc
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise CredentialsError("missing sub")
    return sub
