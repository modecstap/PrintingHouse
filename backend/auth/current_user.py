"""Bearer token username resolution."""

from backend.auth.config import AuthConfig
from backend.auth.errors import CredentialsError
from backend.auth.tokens import decode_access_token


def username_from_token(token: str, config: AuthConfig) -> str:
    """Resolves the username from a JWT without a database lookup.

    :param token:
    :param config:

    :raises CredentialsError: when the token is invalid.

    :return: username from ``sub``.
    """
    try:
        return decode_access_token(token, config)
    except CredentialsError:
        raise
