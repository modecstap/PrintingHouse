from backend.auth.config import AuthConfig
from backend.auth.current_user import username_from_token
from backend.auth.tokens import create_access_token


def test_username_from_token_matches_sub():
    cfg = AuthConfig("k", "HS256", 10)
    token = create_access_token("bob", cfg)
    assert username_from_token(token, cfg) == "bob"
