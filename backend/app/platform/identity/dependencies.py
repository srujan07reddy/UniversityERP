from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException
from app.database.dependencies import get_db
from app.platform.identity.models import User
from app.platform.identity.services import UserIdentityService

bearer_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_security),
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency extracting and validating the Bearer JWT access token.
    Resolves the active, authenticated User entity or raises 401 AuthenticationException.
    """
    if not credentials or not credentials.credentials:
        raise AuthenticationException("Authorization header with Bearer token is required.")
    token = credentials.credentials
    service = UserIdentityService(session)
    return await service.get_current_user_from_token(token)

