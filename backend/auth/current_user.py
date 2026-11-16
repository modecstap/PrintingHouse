"""Bearer token username resolution."""

from backend.auth.config import AuthConfig
from backend.auth.tokens import decode_access_token


__all__ = ["username_from_token"]

def username_from_token(token: str, config: AuthConfig) -> str:
    """Resolves the username from a JWT without a database lookup.

    :param token: the token.
    :param config: runtime configuration.

    :raises CredentialsError: when the token is invalid.

    :return: the str result.
    """
    return decode_access_token(token, config)
