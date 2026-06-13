from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.models.permission import Permission
from backend.server.auth import AuthService
from backend.storage.repositories.user_repository import UserRepository

security = HTTPBearer()


async def get_current_user_with_read_permission(
        credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Зависимость для проверки, что пользователь имеет права READ.
    Используется на всех защищённых эндпоинтах кроме auth.
    """
    auth_service = AuthService(UserRepository())

    user = await auth_service.get_current_user(credentials.credentials)

    if user.permissions != Permission.READ and user.permissions != Permission.FULL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have READ permissions to access this resource",
        )

    return user

async def get_current_user_with_full_permission(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Зависимость для проверки, что пользователь имеет права FULL.
    Используется на всех защищённых эндпоинтах кроме auth.
    """
    auth_service = AuthService(UserRepository())
    
    user = await auth_service.get_current_user(credentials.credentials)
    
    if user.permissions != Permission.FULL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have FULL permissions to access this resource",
        )
    
    return user
