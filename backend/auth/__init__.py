"""Authentication: hashing, JWT, login, and admin seed."""

from backend.auth.config import AuthConfig
from backend.auth.current_user import username_from_token
from backend.auth.errors import (
    AdminSeedConfigError,
    CredentialsError,
    InvalidCredentials,
    MissingJwtSecret,
)
from backend.auth.login import login
from backend.auth.seed import seed_admin_if_empty
from backend.auth.users import StoredUser, UserStore

__all__ = [
    "AdminSeedConfigError",
    "AuthConfig",
    "CredentialsError",
    "InvalidCredentials",
    "MissingJwtSecret",
    "StoredUser",
    "UserStore",
    "login",
    "seed_admin_if_empty",
    "username_from_token",
]
