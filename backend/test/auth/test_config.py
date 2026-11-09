import pytest

from backend.auth.config import AuthConfig
from backend.auth.errors import MissingJwtSecret


def test_from_env_without_secret_raises(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(MissingJwtSecret):
        AuthConfig.from_env()


def test_from_env_defaults_algorithm_and_expire(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "s")
    monkeypatch.delenv("JWT_ALGORITHM", raising=False)
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
    cfg = AuthConfig.from_env()
    assert cfg.algorithm == "HS256"
    assert cfg.access_token_expire_minutes == 1440
