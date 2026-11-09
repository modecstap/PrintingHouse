"""JWT settings from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass

from backend.auth.errors import MissingJwtSecret


@dataclass(frozen=True, slots=True)
class AuthConfig:
    """Signing key, algorithm, and access-token lifetime."""

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    @classmethod
    def from_env(cls) -> AuthConfig:
        """Builds config from documented environment variables.

        :raises MissingJwtSecret: if ``JWT_SECRET_KEY`` is missing or empty.

        :return: validated auth settings.
        """
        secret = os.getenv("JWT_SECRET_KEY")
        if not secret:
            raise MissingJwtSecret("JWT_SECRET_KEY is missing or empty")
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        expire = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
        return cls(
            secret_key=secret,
            algorithm=algorithm,
            access_token_expire_minutes=expire,
        )
