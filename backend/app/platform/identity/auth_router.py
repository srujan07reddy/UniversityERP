from typing import Optional
from fastapi import APIRouter, Depends, Header, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException
from app.core.logging import get_correlation_id
from app.database.dependencies import get_db
from app.platform.identity.dependencies import bearer_security, get_current_user
from app.platform.identity.models import User
from app.platform.identity.schemas import (
    IdentityFootprintResponse,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
    TokenRevokeRequest,
    UserResponse,
)
from app.platform.identity.services import UserIdentityService
from app.schemas.response import APIResponse, MessageResponse

router = APIRouter(prefix="/auth", tags=["Authentication & Sessions"])


def get_identity_service(session: AsyncSession = Depends(get_db)) -> UserIdentityService:
    return UserIdentityService(session)


def get_client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Institutional User Login",
)
async def login(
    data: LoginRequest,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[TokenResponse]:
    """
    Authenticates user credentials and issues access & refresh tokens.
    Implements Argon2id password verification, brute-force protection, and audit logging.
    """
    ip_address = get_client_ip(request)
    tokens = await service.authenticate(data, ip_address=ip_address)
    await service.session.commit()

    return APIResponse(
        success=True,
        data=tokens,
        message="Authentication successful.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Rotate Refresh Token & Renew Access",
)
async def refresh_token(
    data: RefreshTokenRequest,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[TokenResponse]:
    """
    Rotates an active refresh token, issuing a fresh access/refresh token pair.
    """
    ip_address = get_client_ip(request)
    tokens = await service.refresh_tokens(
        refresh_token_str=data.refresh_token,
        device_info=data.device_info,
        ip_address=ip_address,
    )
    await service.session.commit()

    return APIResponse(
        success=True,
        data=tokens,
        message="Token refreshed successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Invalidate Session & Logout",
)
async def logout(
    request: Request,
    data: Optional[LogoutRequest] = None,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_security),
    service: UserIdentityService = Depends(get_identity_service),
) -> MessageResponse:
    """
    Blacklists the active access token JTI and invalidates the associated refresh token.
    """
    if not credentials or not credentials.credentials:
        raise AuthenticationException("Authorization Bearer token required for logout.")

    refresh_token_str = data.refresh_token if data else None
    await service.logout(
        access_token_str=credentials.credentials,
        refresh_token_str=refresh_token_str,
    )
    await service.session.commit()

    return MessageResponse(
        success=True,
        message="Successfully logged out. Session tokens invalidated.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Authenticated User Identity Profile",
)
async def get_me(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserResponse]:
    """
    Retrieves the currently authenticated user's core identity profile.
    """
    return APIResponse(
        success=True,
        data=UserResponse.model_validate(current_user),
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/footprint",
    response_model=APIResponse[IdentityFootprintResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Current User's Institutional Footprint",
)
async def get_my_footprint(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[IdentityFootprintResponse]:
    """
    Retrieves full consolidated institutional identity footprint of the authenticated user.
    """
    footprint = await service.get_identity_footprint(current_user.id)
    return APIResponse(
        success=True,
        data=footprint,
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/revoke",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke Token Explicitly",
)
async def revoke_token(
    data: TokenRevokeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserIdentityService = Depends(get_identity_service),
) -> MessageResponse:
    """
    Administrative or explicit revocation of a specific access or refresh token.
    """
    await service.revoke_token(
        token_str=data.token,
        reason=data.reason,
        performed_by_id=current_user.id,
    )
    await service.session.commit()

    return MessageResponse(
        success=True,
        message="Token has been successfully revoked.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )

