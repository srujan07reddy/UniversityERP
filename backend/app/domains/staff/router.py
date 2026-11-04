import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_correlation_id
from app.database.dependencies import get_db
from app.domains.staff.schemas import (
    StaffCreate,
    StaffDepartmentAffiliationCreate,
    StaffDepartmentAffiliationResponse,
    StaffDepartmentTransfer,
    StaffDesignationUpdate,
    StaffDetailResponse,
    StaffExperienceCreate,
    StaffExperienceResponse,
    StaffQualificationCreate,
    StaffQualificationResponse,
    StaffResponse,
    StaffStatusUpdate,
    StaffUpdate,
)
from app.domains.staff.services import StaffService
from app.schemas.response import APIResponse, MessageResponse, PaginatedResponse, PaginationMetadata

router = APIRouter(prefix="/staff", tags=["Staff Identity & Human Resources"])


def get_staff_service(session: AsyncSession = Depends(get_db)) -> StaffService:
    return StaffService(session)


# ==============================================================================
# Staff Registration & Profiles
# ==============================================================================

@router.post(
    "",
    response_model=APIResponse[StaffResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Appoint / Register New Staff Member",
)
async def create_staff(
    data: StaffCreate,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> APIResponse[StaffResponse]:
    staff = await service.create_staff(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StaffResponse.model_validate(staff),
        message="Staff member appointed and registered successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "",
    response_model=PaginatedResponse[StaffResponse],
    status_code=status.HTTP_200_OK,
    summary="List Staff Members with Filters",
)
async def list_staff(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    department_id: Optional[uuid.UUID] = Query(None, description="Filter by department"),
    school_id: Optional[uuid.UUID] = Query(None, description="Filter by school"),
    staff_type: Optional[str] = Query(None, description="Filter by staff type (TEACHING, NON_TEACHING, etc.)"),
    employment_status: Optional[str] = Query(None, description="Filter by status (ACTIVE, ON_LEAVE, etc.)"),
    search: Optional[str] = Query(None, description="Search by name, employee code, or designation"),
    service: StaffService = Depends(get_staff_service),
) -> PaginatedResponse[StaffResponse]:
    offset = (page - 1) * page_size
    items, total = await service.list_staff(
        offset=offset,
        limit=page_size,
        department_id=department_id,
        school_id=school_id,
        staff_type=staff_type,
        employment_status=employment_status,
        search=search,
    )
    metadata = PaginationMetadata.create(page=page, page_size=page_size, total_items=total)
    return PaginatedResponse(
        success=True,
        data=[StaffResponse.model_validate(item) for item in items],
        pagination=metadata,
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/{staff_id}",
    response_model=APIResponse[StaffResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Staff Profile Summary",
)
async def get_staff(
    staff_id: uuid.UUID,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> APIResponse[StaffResponse]:
    staff = await service.get_staff(staff_id)
    return APIResponse(
        success=True,
        data=StaffResponse.model_validate(staff),
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/{staff_id}/detail",
    response_model=APIResponse[StaffDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Full Staff Dossier",
)
async def get_staff_detail(
    staff_id: uuid.UUID,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> APIResponse[StaffDetailResponse]:
    staff = await service.get_staff_detail(staff_id)
    return APIResponse(
        success=True,
        data=StaffDetailResponse.model_validate(staff),
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.patch(
    "/{staff_id}",
    response_model=APIResponse[StaffResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Staff Details",
)
async def update_staff(
    staff_id: uuid.UUID,
    data: StaffUpdate,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> APIResponse[StaffResponse]:
    staff = await service.update_staff(staff_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StaffResponse.model_validate(staff),
        message="Staff profile updated successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


# ==============================================================================
# Lifecycle Actions: Status, Designation, Transfer
# ==============================================================================

@router.post(
    "/{staff_id}/status",
    response_model=APIResponse[StaffResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Employment Lifecycle Status",
)
async def update_staff_status(
    staff_id: uuid.UUID,
    data: StaffStatusUpdate,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> APIResponse[StaffResponse]:
    staff = await service.update_staff_status(staff_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StaffResponse.model_validate(staff),
        message=f"Staff employment status transitioned to {staff.employment_status}.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/{staff_id}/designation",
    response_model=APIResponse[StaffResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Staff Institutional Designation",
)
async def update_staff_designation(
    staff_id: uuid.UUID,
    data: StaffDesignationUpdate,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> APIResponse[StaffResponse]:
    staff = await service.update_designation(staff_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StaffResponse.model_validate(staff),
        message=f"Staff designation updated to {staff.designation}.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/{staff_id}/transfer",
    response_model=APIResponse[StaffResponse],
    status_code=status.HTTP_200_OK,
    summary="Transfer Staff to Another Department",
)
async def transfer_department(
    staff_id: uuid.UUID,
    data: StaffDepartmentTransfer,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> APIResponse[StaffResponse]:
    staff = await service.transfer_department(staff_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StaffResponse.model_validate(staff),
        message="Staff transferred to new department successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


# ==============================================================================
# Qualifications & Experience
# ==============================================================================

@router.post(
    "/{staff_id}/qualifications",
    response_model=APIResponse[StaffQualificationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Academic or Professional Qualification",
)
async def add_qualification(
    staff_id: uuid.UUID,
    data: StaffQualificationCreate,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> APIResponse[StaffQualificationResponse]:
    qual = await service.add_qualification(staff_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StaffQualificationResponse.model_validate(qual),
        message="Staff qualification recorded successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/{staff_id}/experience",
    response_model=APIResponse[StaffExperienceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Previous Employment Experience",
)
async def add_experience(
    staff_id: uuid.UUID,
    data: StaffExperienceCreate,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> APIResponse[StaffExperienceResponse]:
    exp = await service.add_experience(staff_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StaffExperienceResponse.model_validate(exp),
        message="Previous employment experience record added successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


# ==============================================================================
# Department Affiliations (Secondary / Joint Appointments)
# ==============================================================================

@router.post(
    "/{staff_id}/affiliations",
    response_model=APIResponse[StaffDepartmentAffiliationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Secondary / Joint Department Affiliation",
)
async def add_department_affiliation(
    staff_id: uuid.UUID,
    data: StaffDepartmentAffiliationCreate,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> APIResponse[StaffDepartmentAffiliationResponse]:
    aff = await service.add_department_affiliation(staff_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StaffDepartmentAffiliationResponse.model_validate(aff),
        message="Department affiliation recorded successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/{staff_id}/affiliations",
    response_model=APIResponse[List[StaffDepartmentAffiliationResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Staff Department Affiliations",
)
async def list_department_affiliations(
    staff_id: uuid.UUID,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> APIResponse[List[StaffDepartmentAffiliationResponse]]:
    affs = await service.list_department_affiliations(staff_id)
    return APIResponse(
        success=True,
        data=[StaffDepartmentAffiliationResponse.model_validate(a) for a in affs],
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.delete(
    "/affiliations/{affiliation_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove Department Affiliation",
)
async def remove_department_affiliation(
    affiliation_id: uuid.UUID,
    request: Request,
    service: StaffService = Depends(get_staff_service),
) -> MessageResponse:
    await service.remove_department_affiliation(affiliation_id)
    await service.session.commit()
    return MessageResponse(
        success=True,
        message="Department affiliation removed successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )

