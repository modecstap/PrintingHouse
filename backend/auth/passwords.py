"""Argon2 password hashing."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hashes a plain password for storage.

    :param password:

    :return: encoded password hash.
    """
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Checks a plain password against a stored hash.

    :param password:
    :param password_hash:

    :return: ``True`` when the password matches.
    """
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
