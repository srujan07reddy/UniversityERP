import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_correlation_id
from app.database.dependencies import get_db
from app.platform.identity.schemas import (
    IdentityFootprintResponse,
    UserActionReasonRequest,
    UserCreate,
    UserLifecycleEventResponse,
    UserLinkStaffRequest,
    UserLinkStudentRequest,
    UserOrganizationMembershipCreate,
    UserOrganizationMembershipResponse,
    UserPasswordChange,
    UserPasswordResetConfirm,
    UserPasswordResetRequest,
    UserProfileResponse,
    UserProfileUpdate,
    UserResponse,
    UserStatusUpdate,
    UserUpdate,
)
from app.domains.students.schemas import StudentResponse
from app.domains.staff.schemas import StaffResponse
from app.platform.identity.services import UserIdentityService
from app.schemas.response import APIResponse, MessageResponse, PaginatedResponse, PaginationMetadata

router = APIRouter(prefix="/identity", tags=["User Identity & Accounts"])


def get_identity_service(session: AsyncSession = Depends(get_db)) -> UserIdentityService:
    return UserIdentityService(session)


# ==============================================================================
# User Account Endpoints
# ==============================================================================

@router.post(
    "/users",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register Institutional User",
)
async def create_user(
    data: UserCreate,
    request: Request,
    auto_activate: bool = Query(False, description="Automatically activate without email confirmation"),
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[UserResponse]:
    user, activation_token = await service.create_user(data, auto_activate=auto_activate)
    await service.session.commit()

    res = APIResponse(
        success=True,
        data=UserResponse.model_validate(user),
        message="Institutional user registered successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )
    # Expose activation token in response envelope message or extra header for dev/testing
    if activation_token:
        res.message = f"User registered. Activation token: {activation_token}"
    return res


@router.get(
    "/users/{user_id}",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get User Identity by ID",
)
async def get_user(
    user_id: uuid.UUID,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[UserResponse]:
    user = await service.get_user(user_id)
    return APIResponse(
        success=True,
        data=UserResponse.model_validate(user),
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.patch(
    "/users/{user_id}/status",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Account Status (Activate/Suspend/Deactivate/Reinstate)",
)
async def update_account_status(
    user_id: uuid.UUID,
    data: UserStatusUpdate,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[UserResponse]:
    user = await service.update_account_status(
        user_id=user_id,
        new_status=data.account_status,
        reason=data.reason,
    )
    await service.session.commit()
    fresh_user = await service.get_user(user.id)
    return APIResponse(
        success=True,
        data=UserResponse.model_validate(fresh_user),
        message=f"Account status updated to '{fresh_user.account_status}'.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.patch(
    "/users/{user_id}/profile",
    response_model=APIResponse[UserProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="Update User Profile",
)
async def update_profile(
    user_id: uuid.UUID,
    data: UserProfileUpdate,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[UserProfileResponse]:
    profile = await service.update_profile(user_id=user_id, data=data)
    await service.session.commit()
    fresh_profile = await service.profile_repo.get_by_id(profile.id)
    return APIResponse(
        success=True,
        data=UserProfileResponse.model_validate(fresh_profile),
        message="User profile updated successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/users/{user_id}/password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change User Password",
)
async def change_password(
    user_id: uuid.UUID,
    data: UserPasswordChange,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> MessageResponse:
    await service.change_password(
        user_id=user_id,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    await service.session.commit()
    return MessageResponse(
        success=True,
        message="Password updated successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/users/activate",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Activate User Account with Token",
)
async def activate_account(
    token: str = Query(..., description="Secure activation token"),
    request: Request = None,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[UserResponse]:
    user = await service.activate_account(token)
    await service.session.commit()
    fresh_user = await service.get_user(user.id)
    return APIResponse(
        success=True,
        data=UserResponse.model_validate(fresh_user),
        message="Account activated successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/users/password-reset/request",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset",
)
async def request_password_reset(
    data: UserPasswordResetRequest,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> MessageResponse:
    raw_token = await service.request_password_reset(data.identifier)
    await service.session.commit()

    msg = "If the account exists and is eligible, password recovery instructions have been sent."
    if raw_token:
        # In development/test mode, expose the token in the message for end-to-end verification
        msg += f" (Test Token: {raw_token})"

    return MessageResponse(
        success=True,
        message=msg,
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/users/password-reset/confirm",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm Password Reset",
)
async def confirm_password_reset(
    data: UserPasswordResetConfirm,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> MessageResponse:
    await service.confirm_password_reset(
        raw_token=data.token,
        new_password=data.new_password,
    )
    await service.session.commit()
    return MessageResponse(
        success=True,
        message="Password has been reset successfully. You may now log in.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/users/{user_id}/lifecycle",
    response_model=APIResponse[List[UserLifecycleEventResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get User Identity Lifecycle Audit Events",
)
async def get_user_lifecycle(
    user_id: uuid.UUID,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[List[UserLifecycleEventResponse]]:
    events = await service.get_lifecycle_history(user_id)
    return APIResponse(
        success=True,
        data=[UserLifecycleEventResponse.model_validate(e) for e in events],
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/users/{user_id}/suspend",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Suspend User Account",
)
async def suspend_user(
    user_id: uuid.UUID,
    data: UserActionReasonRequest,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[UserResponse]:
    user = await service.suspend_user(
        user_id=user_id,
        reason=data.reason,
        performed_by_id=data.performed_by_id,
    )
    await service.session.commit()
    fresh_user = await service.get_user(user.id)
    return APIResponse(
        success=True,
        data=UserResponse.model_validate(fresh_user),
        message=f"User account '{fresh_user.username}' has been suspended.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/users/{user_id}/reinstate",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Reinstate User Account",
)
async def reinstate_user(
    user_id: uuid.UUID,
    data: UserActionReasonRequest,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[UserResponse]:
    user = await service.reinstate_user(
        user_id=user_id,
        reason=data.reason,
        performed_by_id=data.performed_by_id,
    )
    await service.session.commit()
    fresh_user = await service.get_user(user.id)
    return APIResponse(
        success=True,
        data=UserResponse.model_validate(fresh_user),
        message=f"User account '{fresh_user.username}' has been reinstated to ACTIVE status.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/users/{user_id}/deactivate",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Deactivate User Account Safely",
)
async def deactivate_user(
    user_id: uuid.UUID,
    data: UserActionReasonRequest,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[UserResponse]:
    user = await service.deactivate_user(
        user_id=user_id,
        reason=data.reason,
        performed_by_id=data.performed_by_id,
    )
    await service.session.commit()
    fresh_user = await service.get_user(user.id)
    return APIResponse(
        success=True,
        data=UserResponse.model_validate(fresh_user),
        message=f"User account '{fresh_user.username}' deactivated. Academic and employment records preserved.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/users/{user_id}/unlock",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Unlock User Account",
)
async def unlock_user(
    user_id: uuid.UUID,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[UserResponse]:
    user = await service.unlock_user(user_id=user_id)
    await service.session.commit()
    fresh_user = await service.get_user(user.id)
    return APIResponse(
        success=True,
        data=UserResponse.model_validate(fresh_user),
        message=f"User account '{fresh_user.username}' unlocked successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/lifecycle/events",
    response_model=PaginatedResponse[UserLifecycleEventResponse],
    status_code=status.HTTP_200_OK,
    summary="Search Institutional Identity Audit Trail",
)
async def list_lifecycle_events(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    from_date: Optional[datetime] = Query(None, description="Filter from timestamp"),
    to_date: Optional[datetime] = Query(None, description="Filter to timestamp"),
    service: UserIdentityService = Depends(get_identity_service),
) -> PaginatedResponse[UserLifecycleEventResponse]:
    offset = (page - 1) * page_size
    items, total = await service.list_lifecycle_events(
        offset=offset,
        limit=page_size,
        user_id=user_id,
        event_type=event_type,
        from_date=from_date,
        to_date=to_date,
    )
    metadata = PaginationMetadata.create(page=page, page_size=page_size, total_items=total)
    return PaginatedResponse(
        success=True,
        data=[UserLifecycleEventResponse.model_validate(item) for item in items],
        pagination=metadata,
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


# ==============================================================================
# Identity Relationships Endpoints (Stage 3.5)
# ==============================================================================

@router.post(
    "/relationships/link-student",
    response_model=APIResponse[StudentResponse],
    status_code=status.HTTP_200_OK,
    summary="Link User to Student Identity",
)
async def link_student(
    data: UserLinkStudentRequest,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[StudentResponse]:
    student = await service.link_student(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StudentResponse.model_validate(student),
        message=f"User identity successfully linked to student '{student.admission_number}'.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.delete(
    "/relationships/unlink-student/{student_id}",
    response_model=APIResponse[StudentResponse],
    status_code=status.HTTP_200_OK,
    summary="Unlink User from Student Identity",
)
async def unlink_student(
    student_id: uuid.UUID,
    request: Request,
    reason: Optional[str] = Query(None, description="Administrative reason for unlinking"),
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[StudentResponse]:
    student = await service.unlink_student(student_id, reason=reason)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StudentResponse.model_validate(student),
        message=f"Student '{student.admission_number}' unlinked from user account.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/relationships/link-staff",
    response_model=APIResponse[StaffResponse],
    status_code=status.HTTP_200_OK,
    summary="Link User to Staff Identity",
)
async def link_staff(
    data: UserLinkStaffRequest,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[StaffResponse]:
    staff = await service.link_staff(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StaffResponse.model_validate(staff),
        message=f"User identity successfully linked to staff member '{staff.staff_id}'.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.delete(
    "/relationships/unlink-staff/{staff_id}",
    response_model=APIResponse[StaffResponse],
    status_code=status.HTTP_200_OK,
    summary="Unlink User from Staff Identity",
)
async def unlink_staff(
    staff_id: uuid.UUID,
    request: Request,
    reason: Optional[str] = Query(None, description="Administrative reason for unlinking"),
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[StaffResponse]:
    staff = await service.unlink_staff(staff_id, reason=reason)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StaffResponse.model_validate(staff),
        message=f"Staff member '{staff.staff_id}' unlinked from user account.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/relationships/memberships/user/{user_id}",
    response_model=APIResponse[UserOrganizationMembershipResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Grant User Organizational Membership",
)
async def add_organization_membership(
    user_id: uuid.UUID,
    data: UserOrganizationMembershipCreate,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[UserOrganizationMembershipResponse]:
    membership = await service.add_organization_membership(user_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=UserOrganizationMembershipResponse.model_validate(membership),
        message="Organizational membership granted successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/relationships/memberships/user/{user_id}",
    response_model=APIResponse[List[UserOrganizationMembershipResponse]],
    status_code=status.HTTP_200_OK,
    summary="List User Organizational Memberships",
)
async def list_user_memberships(
    user_id: uuid.UUID,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[List[UserOrganizationMembershipResponse]]:
    memberships = await service.list_user_memberships(user_id)
    return APIResponse(
        success=True,
        data=[UserOrganizationMembershipResponse.model_validate(m) for m in memberships],
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.delete(
    "/relationships/memberships/{membership_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke User Organizational Membership",
)
async def remove_organization_membership(
    membership_id: uuid.UUID,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> MessageResponse:
    await service.remove_organization_membership(membership_id)
    await service.session.commit()
    return MessageResponse(
        success=True,
        message="Organizational membership revoked successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/relationships/footprint/{user_id}",
    response_model=APIResponse[IdentityFootprintResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Consolidated Institutional Identity Footprint",
)
async def get_identity_footprint(
    user_id: uuid.UUID,
    request: Request,
    service: UserIdentityService = Depends(get_identity_service),
) -> APIResponse[IdentityFootprintResponse]:
    footprint = await service.get_identity_footprint(user_id)
    return APIResponse(
        success=True,
        data=footprint,
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )

