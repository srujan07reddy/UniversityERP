import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_correlation_id
from app.database.dependencies import get_db
from app.platform.organization.schemas import (
    AcademicBatchCreate,
    AcademicBatchResponse,
    AcademicProgramCreate,
    AcademicProgramResponse,
    AcademicYearCreate,
    AcademicYearResponse,
    CourseCreate,
    CourseResponse,
    OrganizationalRelationshipCreate,
    OrganizationalRelationshipResponse,
    OrganizationalUnitCreate,
    OrganizationalUnitResponse,
    OrganizationalUnitTreeResponse,
    SectionCreate,
    SectionResponse,
    SemesterCreate,
    SemesterResponse,
    SpecializationCreate,
    SpecializationResponse,
    UniversityCreate,
    UniversityResponse,
)
from app.platform.organization.services import OrganizationService
from app.schemas.response import APIResponse

router = APIRouter(prefix="/organization", tags=["Institutional Organization"])


def get_org_service(session: AsyncSession = Depends(get_db)) -> OrganizationService:
    return OrganizationService(session)


# ==============================================================================
# Universities
# ==============================================================================

@router.post(
    "/universities",
    response_model=APIResponse[UniversityResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create University Charter",
)
async def create_university(
    data: UniversityCreate,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[UniversityResponse]:
    univ = await service.create_university(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=UniversityResponse.model_validate(univ),
        message="University charter created successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/universities/{university_id}",
    response_model=APIResponse[UniversityResponse],
    status_code=status.HTTP_200_OK,
    summary="Get University by ID",
)
async def get_university(
    university_id: uuid.UUID,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[UniversityResponse]:
    univ = await service.get_university(university_id)
    return APIResponse(
        success=True,
        data=UniversityResponse.model_validate(univ),
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/universities",
    response_model=APIResponse[List[UniversityResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Universities",
)
async def list_universities(
    request: Request,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[List[UniversityResponse]]:
    universities = await service.list_universities(offset=offset, limit=limit)
    return APIResponse(
        success=True,
        data=[UniversityResponse.model_validate(u) for u in universities],
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


# ==============================================================================
# Organizational Units (Schools, Departments, Functional Units)
# ==============================================================================

@router.post(
    "/units",
    response_model=APIResponse[OrganizationalUnitResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Organizational Unit",
)
async def create_unit(
    data: OrganizationalUnitCreate,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[OrganizationalUnitResponse]:
    unit = await service.create_unit(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=OrganizationalUnitResponse.model_validate(unit),
        message="Organizational unit established successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/units/tree",
    response_model=APIResponse[List[OrganizationalUnitTreeResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get Complete Organization Tree",
)
async def get_organization_tree(
    university_id: uuid.UUID,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[List[OrganizationalUnitTreeResponse]]:
    tree = await service.get_organization_tree(university_id)
    return APIResponse(
        success=True,
        data=tree,
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/units/{unit_id}",
    response_model=APIResponse[OrganizationalUnitResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Organizational Unit by ID",
)
async def get_unit(
    unit_id: uuid.UUID,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[OrganizationalUnitResponse]:
    unit = await service.get_unit(unit_id)
    return APIResponse(
        success=True,
        data=OrganizationalUnitResponse.model_validate(unit),
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/units",
    response_model=APIResponse[List[OrganizationalUnitResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Organizational Units",
)
async def list_units(
    university_id: uuid.UUID,
    request: Request,
    unit_type: Optional[str] = Query(None, description="Filter by SCHOOL, DEPARTMENT, etc."),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[List[OrganizationalUnitResponse]]:
    units = await service.list_units(university_id=university_id, unit_type=unit_type, offset=offset, limit=limit)
    return APIResponse(
        success=True,
        data=[OrganizationalUnitResponse.model_validate(u) for u in units],
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


# ==============================================================================
# Non-Hierarchical Organizational Relationships
# ==============================================================================

@router.post(
    "/relationships",
    response_model=APIResponse[OrganizationalRelationshipResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Define Cross-Unit Relationship",
)
async def create_relationship(
    data: OrganizationalRelationshipCreate,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[OrganizationalRelationshipResponse]:
    rel = await service.create_relationship(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=OrganizationalRelationshipResponse.model_validate(rel),
        message="Organizational relationship established.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/units/{unit_id}/relationships",
    response_model=APIResponse[List[OrganizationalRelationshipResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Unit Relationships",
)
async def list_unit_relationships(
    unit_id: uuid.UUID,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[List[OrganizationalRelationshipResponse]]:
    rels = await service.list_unit_relationships(unit_id)
    return APIResponse(
        success=True,
        data=[OrganizationalRelationshipResponse.model_validate(r) for r in rels],
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


# ==============================================================================
# Academic Years & Semesters
# ==============================================================================

@router.post(
    "/academic-years",
    response_model=APIResponse[AcademicYearResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Academic Year",
)
async def create_academic_year(
    data: AcademicYearCreate,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[AcademicYearResponse]:
    ay = await service.create_academic_year(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=AcademicYearResponse.model_validate(ay),
        message="Academic year created successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/semesters",
    response_model=APIResponse[SemesterResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Semester Session",
)
async def create_semester(
    data: SemesterCreate,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[SemesterResponse]:
    sem = await service.create_semester(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=SemesterResponse.model_validate(sem),
        message="Semester session created successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/academic-years/{academic_year_id}/semesters",
    response_model=APIResponse[List[SemesterResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Semesters in Academic Year",
)
async def list_semesters_for_year(
    academic_year_id: uuid.UUID,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[List[SemesterResponse]]:
    sems = await service.list_semesters_for_year(academic_year_id)
    return APIResponse(
        success=True,
        data=[SemesterResponse.model_validate(s) for s in sems],
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


# ==============================================================================
# Academic Programs & Specializations
# ==============================================================================

@router.post(
    "/programs",
    response_model=APIResponse[AcademicProgramResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Academic Degree Program",
)
async def create_program(
    data: AcademicProgramCreate,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[AcademicProgramResponse]:
    prog = await service.create_program(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=AcademicProgramResponse.model_validate(prog),
        message="Academic program registered successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/programs/{program_id}",
    response_model=APIResponse[AcademicProgramResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Academic Program by ID",
)
async def get_program(
    program_id: uuid.UUID,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[AcademicProgramResponse]:
    prog = await service.get_program(program_id)
    return APIResponse(
        success=True,
        data=AcademicProgramResponse.model_validate(prog),
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/departments/{department_id}/programs",
    response_model=APIResponse[List[AcademicProgramResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Programs for Department",
)
async def list_programs_for_department(
    department_id: uuid.UUID,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[List[AcademicProgramResponse]]:
    progs = await service.list_programs_for_department(department_id)
    return APIResponse(
        success=True,
        data=[AcademicProgramResponse.model_validate(p) for p in progs],
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/specializations",
    response_model=APIResponse[SpecializationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Program Specialization",
)
async def create_specialization(
    data: SpecializationCreate,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[SpecializationResponse]:
    spec = await service.create_specialization(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=SpecializationResponse.model_validate(spec),
        message="Specialization created successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


# ==============================================================================
# Courses
# ==============================================================================

@router.post(
    "/courses",
    response_model=APIResponse[CourseResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Catalog Course",
)
async def create_course(
    data: CourseCreate,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[CourseResponse]:
    course = await service.create_course(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=CourseResponse.model_validate(course),
        message="Course registered in catalog successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/courses/{course_id}",
    response_model=APIResponse[CourseResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Course by ID",
)
async def get_course(
    course_id: uuid.UUID,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[CourseResponse]:
    course = await service.get_course(course_id)
    return APIResponse(
        success=True,
        data=CourseResponse.model_validate(course),
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/departments/{department_id}/courses",
    response_model=APIResponse[List[CourseResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Courses for Department",
)
async def list_courses_for_department(
    department_id: uuid.UUID,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[List[CourseResponse]]:
    courses = await service.list_courses_for_department(department_id)
    return APIResponse(
        success=True,
        data=[CourseResponse.model_validate(c) for c in courses],
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


# ==============================================================================
# Batches & Sections
# ==============================================================================

@router.post(
    "/batches",
    response_model=APIResponse[AcademicBatchResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Academic Student Batch",
)
async def create_batch(
    data: AcademicBatchCreate,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[AcademicBatchResponse]:
    batch = await service.create_batch(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=AcademicBatchResponse.model_validate(batch),
        message="Academic batch registered successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/programs/{program_id}/batches",
    response_model=APIResponse[List[AcademicBatchResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Batches for Program",
)
async def list_batches_for_program(
    program_id: uuid.UUID,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[List[AcademicBatchResponse]]:
    batches = await service.list_batches_for_program(program_id)
    return APIResponse(
        success=True,
        data=[AcademicBatchResponse.model_validate(b) for b in batches],
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.post(
    "/sections",
    response_model=APIResponse[SectionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Batch Section",
)
async def create_section(
    data: SectionCreate,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[SectionResponse]:
    section = await service.create_section(data)
    await service.session.commit()
    return APIResponse(
        success=True,
        data=SectionResponse.model_validate(section),
        message="Batch section created successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/batches/{batch_id}/sections",
    response_model=APIResponse[List[SectionResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Sections for Batch",
)
async def list_sections_for_batch(
    batch_id: uuid.UUID,
    request: Request,
    service: OrganizationService = Depends(get_org_service),
) -> APIResponse[List[SectionResponse]]:
    sections = await service.list_sections_for_batch(batch_id)
    return APIResponse(
        success=True,
        data=[SectionResponse.model_validate(s) for s in sections],
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )
