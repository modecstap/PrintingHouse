from typing import Optional
from sqlalchemy import select

from backend.models.permission import Permission
from backend.storage.repositories.base import BaseRepository
from backend.storage.tables.user import UserEntity
from backend.storage.repositories.wrappers.ensure_session import ensure_session


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserEntity)

    @ensure_session
    async def create(self, username: str, email: str, hashed_password: str, permissions: Permission = Permission.READ, session=None) -> UserEntity:
        user = self._entity(
            username=username,
            email=email,
            hashed_password=hashed_password,
            permissions=permissions,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @ensure_session
    async def get_by_username(self, username: str, session=None) -> Optional[UserEntity]:
        result = await session.execute(select(self._entity).where(self._entity.username == username))
        return result.scalar_one_or_none()

    @ensure_session
    async def get_by_email(self, email: str, session=None) -> Optional[UserEntity]:
        result = await session.execute(select(self._entity).where(self._entity.email == email))
        return result.scalar_one_or_none()

    @ensure_session
    async def update_permissions(self, user_id: int, permissions: Permission, session=None) -> UserEntity:
        result = await session.execute(select(self._entity).where(self._entity.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.permissions = permissions
            await session.commit()
            await session.refresh(user)
        return user
