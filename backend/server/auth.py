"""Login route."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from backend.auth import AuthConfig, InvalidCredentials, login
from backend.server.dependencies import get_auth_config, get_user_store
from backend.server.schemas import LoginRequest, TokenResponse
from backend.storage.user.repository import SqlUserRepository

router = APIRouter()


@router.post("/auth/token", response_model=TokenResponse)
def issue_token(
    body: LoginRequest,
    store: Annotated[SqlUserRepository, Depends(get_user_store)],
    auth_config: Annotated[AuthConfig, Depends(get_auth_config)],
) -> TokenResponse:
    """Exchanges username and password for a JWT.

    :raises HTTPException: 401 on invalid credentials without WWW-Authenticate.
    """
    try:
        token = login(body.username, body.password, store, auth_config)
    except InvalidCredentials:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        ) from None
    return TokenResponse(access_token=token)
