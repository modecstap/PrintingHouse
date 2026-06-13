from datetime import datetime, timedelta
import os

from fastapi import  HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.storage.repositories.user_repository import UserRepository


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        secret_key: str | None = None,
        algorithm: str | None = None,
        access_token_expire_minutes: int | None = None,
    ):
        self._user_repository = user_repository

        self._secret_key = secret_key or os.getenv(
            "JWT_SECRET_KEY",
            "change-me-secret",
        )

        self._algorithm = algorithm or os.getenv(
            "JWT_ALGORITHM",
            "HS256",
        )

        self._access_token_expire_minutes = (
            access_token_expire_minutes
            or int(
                os.getenv(
                    "ACCESS_TOKEN_EXPIRE_MINUTES",
                    60 * 24,
                )
            )
        )

        self._pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
        )

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        return self._pwd_context.verify(
            plain_password,
            hashed_password,
        )

    def get_password_hash(
        self,
        password: str,
    ) -> str:
        return self._pwd_context.hash(password)

    def create_access_token(
        self,
        data: dict,
        expires_delta: timedelta | None = None,
    ) -> str:
        to_encode = data.copy()

        expire = (
            datetime.utcnow() + expires_delta
            if expires_delta
            else datetime.utcnow()
            + timedelta(
                minutes=self._access_token_expire_minutes
            )
        )

        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode,
            self._secret_key,
            algorithm=self._algorithm,
        )

    async def get_current_user(
        self,
        token: str,
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )

            username = payload.get("sub")

            if username is None:
                raise credentials_exception

        except JWTError:
            raise credentials_exception

        user = await self._user_repository.get_by_username(
            username
        )

        if user is None:
            raise credentials_exception

        return user