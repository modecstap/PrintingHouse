from datetime import timedelta

from fastapi import HTTPException, status
from pydantic import EmailStr, BaseModel

from backend.server.auth import AuthService
from backend.storage.repositories.user_repository import UserRepository


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str


class AuthHandler:
    token_response_model = TokenResponse

    def __init__(self):
        self._user_repo = UserRepository()
        self.auth = AuthService(self._user_repo)

    async def register(self, req: RegisterRequest):
        existing = await self._user_repo.get_by_username(req.username)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Username already registered",
            )

        existing_email = await self._user_repo.get_by_email(req.email)
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )

        hashed = self.auth.get_password_hash(req.password)

        user = await self._user_repo.create(
            req.username,
            req.email,
            hashed,
        )

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }

    async def login(self, form: LoginRequest):
        user = await self._user_repo.get_by_username(
            form.username,
        )

        if not user or not self.auth.verify_password(
            form.password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        access_token = self.auth.create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(
                minutes=self.auth._access_token_expire_minutes,
            ),
        )

        return TokenResponse(
            access_token=access_token,
        )