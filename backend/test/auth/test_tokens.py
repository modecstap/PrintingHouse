from datetime import UTC, datetime, timedelta

import jwt
import pytest

from backend.auth.config import AuthConfig
from backend.auth.errors import CredentialsError
from backend.auth.tokens import create_access_token, decode_access_token


def test_token_round_trip_sub():
    cfg = AuthConfig("key", "HS256", 60)
    token = create_access_token("alice", cfg)
    assert decode_access_token(token, cfg) == "alice"


def test_expired_token_is_credentials_error():
    cfg = AuthConfig("key", "HS256", 60)
    expired = datetime.now(UTC) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": "alice", "exp": expired},
        cfg.secret_key,
        algorithm=cfg.algorithm,
    )
    with pytest.raises(CredentialsError):
        decode_access_token(token, cfg)
