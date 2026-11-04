import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_correlation_id
from app.database.dependencies import get_db
from app.domains.students.schemas import (
    StudentAcademicRecordCreate,
    StudentAcademicRecordResponse,
    StudentCreate,
    StudentDetailResponse,
    StudentEnrollmentCreate,
    StudentEnrollmentResponse,
    StudentResponse,
    StudentSectionAssign,
    StudentStatusUpdate,
    StudentUpdate,
)
from app.domains.students.services import StudentService
from app.schemas.response import APIResponse, PaginatedResponse, PaginationMetadata

router = APIRouter(prefix="/students", tags=["Student Identity & Records"])


def get_student_service(session: AsyncSession = Depends(get_db)) -> StudentService:
    return StudentService(session)


# ==============================================================================
# Student Registration & Profiles
# ==============================================================================

@router.post(
    "",
    response_model=APIResponse[StudentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Admit / Register New Student",
)
async def create_student(
    data: StudentCreate,
    request: Request,
    service: StudentService = Depends(get_student_service),
) -> APIResponse[StudentResponse]:
    student = await service.create_student(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StudentResponse.model_validate(student),
        message="Student registered and admitted successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "",
    response_model=PaginatedResponse[StudentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Students with Filters",
)
async def list_students(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    department_id: Optional[uuid.UUID] = Query(None, description="Filter by department"),
    program_id: Optional[uuid.UUID] = Query(None, description="Filter by program"),
    batch_id: Optional[uuid.UUID] = Query(None, description="Filter by batch"),
    section_id: Optional[uuid.UUID] = Query(None, description="Filter by section"),
    student_status: Optional[str] = Query(None, description="Filter by status (ADMITTED, ACTIVE, etc.)"),
    search: Optional[str] = Query(None, description="Search by name or admission/register number"),
    service: StudentService = Depends(get_student_service),
) -> PaginatedResponse[StudentResponse]:
    offset = (page - 1) * page_size
    items, total = await service.list_students(
        offset=offset,
        limit=page_size,
        department_id=department_id,
        program_id=program_id,
        batch_id=batch_id,
        section_id=section_id,
        student_status=student_status,
        search=search,
    )
    metadata = PaginationMetadata.create(page=page, page_size=page_size, total_items=total)
    return PaginatedResponse(
        success=True,
        data=[StudentResponse.model_validate(item) for item in items],
        pagination=metadata,
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/{student_id}",
    response_model=APIResponse[StudentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Student Profile",
)
async def get_student(
    student_id: uuid.UUID,
    request: Request,
    service: StudentService = Depends(get_student_service),
) -> APIResponse[StudentResponse]:
    student = await service.get_student(student_id)
    return APIResponse(
        success=True,
        data=StudentResponse.model_validate(student),
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/{student_id}/detail",
    response_model=APIResponse[StudentDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Full Student Dossier",
)
async def get_student_detail(
    student_id: uuid.UUID,
    request: Request,
    service: StudentService = Depends(get_student_service),
) -> APIResponse[StudentDetailResponse]:
    student = await service.get_student_detail(student_id)
    return APIResponse(
        success=True,
        data=StudentDetailResponse.model_validate(student),
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.patch(
    "/{student_id}",
    response_model=APIResponse[StudentResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Student Details",
)
async def update_student(
    student_id: uuid.UUID,
    data: StudentUpdate,
    request: Request,
    service: StudentService = Depends(get_student_service),
) -> APIResponse[StudentResponse]:
    student = await service.update_student(student_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StudentResponse.model_validate(student),
        message="Student profile updated successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/{student_id}/status",
    response_model=APIResponse[StudentResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Student Lifecycle Status",
)
async def update_student_status(
    student_id: uuid.UUID,
    data: StudentStatusUpdate,
    request: Request,
    service: StudentService = Depends(get_student_service),
) -> APIResponse[StudentResponse]:
    student = await service.update_student_status(student_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StudentResponse.model_validate(student),
        message=f"Student lifecycle status transitioned to {student.student_status}.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/{student_id}/assign-section",
    response_model=APIResponse[StudentResponse],
    status_code=status.HTTP_200_OK,
    summary="Assign Batch & Section",
)
async def assign_section(
    student_id: uuid.UUID,
    data: StudentSectionAssign,
    request: Request,
    service: StudentService = Depends(get_student_service),
) -> APIResponse[StudentResponse]:
    student = await service.assign_section(student_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StudentResponse.model_validate(student),
        message="Student batch and section assigned successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


# ==============================================================================
# Academic Records & Enrollments
# ==============================================================================

@router.post(
    "/{student_id}/academic-records",
    response_model=APIResponse[StudentAcademicRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Previous Academic Qualification Record",
)
async def add_academic_record(
    student_id: uuid.UUID,
    data: StudentAcademicRecordCreate,
    request: Request,
    service: StudentService = Depends(get_student_service),
) -> APIResponse[StudentAcademicRecordResponse]:
    record = await service.add_academic_record(student_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StudentAcademicRecordResponse.model_validate(record),
        message="Previous academic record recorded successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/{student_id}/enrollments",
    response_model=APIResponse[StudentEnrollmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register Semester Academic Enrollment",
)
async def create_enrollment(
    student_id: uuid.UUID,
    data: StudentEnrollmentCreate,
    request: Request,
    service: StudentService = Depends(get_student_service),
) -> APIResponse[StudentEnrollmentResponse]:
    enrollment = await service.create_enrollment(student_id, data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=StudentEnrollmentResponse.model_validate(enrollment),
        message=f"Student enrolled in semester {enrollment.semester_number} successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )
