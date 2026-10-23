from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from backend.models.permission import Permission
from backend.server.auth.service import AuthService
from backend.storage.repositories.user_repository import UserRepository


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


router = APIRouter(prefix="/auth", tags=["auth"])
_user_repository = UserRepository()
_auth_service = AuthService(_user_repository)


@router.post("/register", status_code=201, response_model=None)
async def register(req: RegisterRequest) -> dict:
    """Регистрирует пользователя с правами NONE.

    Сначала проверяет имя, потом email: при обоих дублях ответ про имя.
    Результат: словарь id, username, email и permissions.value.
    Побочные эффекты: новая строка пользователя.
    Ошибки: HTTP 400 «Username already registered» или «Email already registered».
    """
    existing = await _user_repository.get_by_username(req.username)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Username already registered",
        )

    existing_email = await _user_repository.get_by_email(req.email)
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    hashed = _auth_service.get_password_hash(req.password)
    user = await _user_repository.create(
        req.username,
        req.email,
        hashed,
        permissions=Permission.NONE,
    )
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "permissions": user.permissions.value,
    }


@router.post("/token", response_model=TokenResponse)
async def login(form: LoginRequest) -> TokenResponse:
    """Выдаёт access token по имени и паролю.

    Результат: TokenResponse. token_type остаётся bearer.
    Ошибки: HTTP 401 «Incorrect username or password», без заголовка WWW-Authenticate.
    """
    user = await _user_repository.get_by_username(form.username)
    if not user or not _auth_service.verify_password(
        form.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = _auth_service.create_access_token(
        data={"sub": user.username, "permissions": user.permissions.value},
        expires_delta=timedelta(minutes=_auth_service._access_token_expire_minutes),
    )
    return TokenResponse(access_token=access_token)
