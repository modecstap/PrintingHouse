"""Tests for server.test_auth_http.py.
"""

__all__ = [
    "test_login_returns_bearer_token",
    "test_wrong_password_401_without_www_authenticate",
    "test_protected_route_without_token_401",
]

def test_login_returns_bearer_token(api_client):
    """Handles test login returns bearer token.

    :param api_client: the api client.
    """
    response = api_client.post(
        "/auth/token",
        json={"username": "tester", "password": "pass"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_wrong_password_401_without_www_authenticate(api_client):
    """Handles test wrong password 401 without www authenticate.

    :param api_client: the api client.
    """
    response = api_client.post(
        "/auth/token",
        json={"username": "tester", "password": "bad"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
    assert "WWW-Authenticate" not in response.headers


def test_protected_route_without_token_401(api_client):
    """Handles test protected route without token 401.

    :param api_client: the api client.
    """
    response = api_client.get("/api/orders")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
    assert response.headers.get("WWW-Authenticate") == "Bearer"
