"""Argon2 password hashing."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

__all__ = [
    "hash_password",
    "verify_password",
]

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hashes a plain password for storage.

    :param password: the password.

    :return: the str result.
    """
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Checks a plain password against a stored hash.

    :param password: the password.
    :param password_hash: the password hash.

    :return: the bool result.
    """
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
