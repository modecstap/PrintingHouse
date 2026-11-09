"""Auth configuration and credential errors."""


class MissingJwtSecret(Exception):
    """Reports that ``JWT_SECRET_KEY`` is missing or empty."""


class AdminSeedConfigError(Exception):
    """Reports that admin seed env is missing while the users table is empty."""


class InvalidCredentials(Exception):
    """Reports a failed login without distinguishing unknown user."""


class CredentialsError(Exception):
    """Reports an invalid or expired bearer token."""
