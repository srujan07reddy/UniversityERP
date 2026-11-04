import uuid
from typing import Any, List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.platform.organization.models import (
    AcademicBatch,
    AcademicProgram,
    AcademicYear,
    Course,
    OrganizationalRelationship,
    OrganizationalUnit,
    Section,
    Semester,
    Specialization,
    University,
)
from app.platform.organization.repositories import (
    AcademicBatchRepository,
    AcademicProgramRepository,
    AcademicYearRepository,
    CourseRepository,
    OrganizationalRelationshipRepository,
    OrganizationalUnitRepository,
    SectionRepository,
    SemesterRepository,
    SpecializationRepository,
    UniversityRepository,
)
from app.platform.organization.schemas import (
    AcademicBatchCreate,
    AcademicProgramCreate,
    AcademicYearCreate,
    CourseCreate,
    OrganizationalRelationshipCreate,
    OrganizationalUnitCreate,
    OrganizationalUnitTreeResponse,
    SectionCreate,
    SemesterCreate,
    SpecializationCreate,
    UniversityCreate,
)


class OrganizationService:
    """
    Central business service coordinating the institutional organizational hierarchy.
    Enforces referential integrity, tree structuring, and domain validation.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.univ_repo = UniversityRepository(session)
        self.unit_repo = OrganizationalUnitRepository(session)
        self.rel_repo = OrganizationalRelationshipRepository(session)
        self.ay_repo = AcademicYearRepository(session)
        self.sem_repo = SemesterRepository(session)
        self.prog_repo = AcademicProgramRepository(session)
        self.spec_repo = SpecializationRepository(session)
        self.course_repo = CourseRepository(session)
        self.batch_repo = AcademicBatchRepository(session)
        self.sec_repo = SectionRepository(session)

    # --------------------------------------------------------------------------
    # University Operations
    # --------------------------------------------------------------------------

    async def create_university(self, data: UniversityCreate) -> University:
        existing = await self.univ_repo.get_by_code(data.code)
        if existing:
            raise ConflictException(f"University with code '{data.code}' already exists.")
        return await self.univ_repo.create(data)

    async def get_university(self, univ_id: uuid.UUID) -> University:
        univ = await self.univ_repo.get_by_id(univ_id)
        if not univ:
            raise NotFoundException(f"University with ID '{univ_id}' not found.")
        return univ

    async def list_universities(self, offset: int = 0, limit: int = 50) -> Sequence[University]:
        return await self.univ_repo.get_multi(offset=offset, limit=limit)

    # --------------------------------------------------------------------------
    # Organizational Unit Operations (Schools, Departments, Functional Units)
    # --------------------------------------------------------------------------

    async def create_unit(self, data: OrganizationalUnitCreate) -> OrganizationalUnit:
        # Verify university exists
        await self.get_university(data.university_id)

        # Check code uniqueness
        existing = await self.unit_repo.get_by_code(data.code)
        if existing:
            raise ConflictException(f"Organizational unit with code '{data.code}' already exists.")

        # If parent_unit_id is provided, verify parent exists and belongs to same university
        if data.parent_unit_id:
            parent = await self.unit_repo.get_by_id(data.parent_unit_id)
            if not parent:
                raise NotFoundException(f"Parent organizational unit '{data.parent_unit_id}' not found.")
            if parent.university_id != data.university_id:
                raise ValidationException("Parent unit must belong to the same university.")

        return await self.unit_repo.create(data)

    async def get_unit(self, unit_id: uuid.UUID) -> OrganizationalUnit:
        unit = await self.unit_repo.get_by_id(unit_id)
        if not unit:
            raise NotFoundException(f"Organizational unit with ID '{unit_id}' not found.")
        return unit

    async def list_units(
        self,
        university_id: uuid.UUID,
        unit_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[OrganizationalUnit]:
        if unit_type:
            return await self.unit_repo.get_by_type(university_id, unit_type)
        return await self.unit_repo.get_multi(offset=offset, limit=limit)

    async def get_organization_tree(self, university_id: uuid.UUID) -> List[OrganizationalUnitTreeResponse]:
        """
        Builds recursive tree of organizational units starting from root units (Schools/Offices).
        """
        root_units = await self.unit_repo.get_root_units(university_id)
        
        async def build_node(unit: OrganizationalUnit) -> OrganizationalUnitTreeResponse:
            children = await self.unit_repo.get_children(unit.id)
            child_nodes = [await build_node(c) for c in children]
            return OrganizationalUnitTreeResponse(
                id=unit.id,
                code=unit.code,
                name=unit.name,
                unit_type=unit.unit_type,
                status=unit.status,
                children=child_nodes,
            )

        return [await build_node(u) for u in root_units]

    # --------------------------------------------------------------------------
    # Explicit Organizational Relationships (Non-Hierarchical)
    # --------------------------------------------------------------------------

    async def create_relationship(self, data: OrganizationalRelationshipCreate) -> OrganizationalRelationship:
        if data.source_unit_id == data.target_unit_id:
            raise ValidationException("Source and target units cannot be identical in a relationship.")
        await self.get_unit(data.source_unit_id)
        await self.get_unit(data.target_unit_id)
        return await self.rel_repo.create(data)

    async def list_unit_relationships(self, unit_id: uuid.UUID) -> Sequence[OrganizationalRelationship]:
        await self.get_unit(unit_id)
        return await self.rel_repo.get_for_unit(unit_id)

    # --------------------------------------------------------------------------
    # Academic Years & Semesters
    # --------------------------------------------------------------------------

    async def create_academic_year(self, data: AcademicYearCreate) -> AcademicYear:
        await self.get_university(data.university_id)
        if data.end_date <= data.start_date:
            raise ValidationException("Academic year end date must be strictly after start date.")
        
        existing = await self.ay_repo.get_by_name(data.university_id, data.year_name)
        if existing:
            raise ConflictException(f"Academic year '{data.year_name}' already exists for this university.")
        
        return await self.ay_repo.create(data)

    async def create_semester(self, data: SemesterCreate) -> Semester:
        ay = await self.ay_repo.get_by_id(data.academic_year_id)
        if not ay:
            raise NotFoundException(f"Academic year '{data.academic_year_id}' not found.")
        if data.end_date <= data.start_date:
            raise ValidationException("Semester end date must be strictly after start date.")
        
        existing = await self.sem_repo.get_by_year_and_number(data.academic_year_id, data.semester_number)
        if existing:
            raise ConflictException(f"Semester number {data.semester_number} already defined for this academic year.")
        
        return await self.sem_repo.create(data)

    async def list_semesters_for_year(self, academic_year_id: uuid.UUID) -> Sequence[Semester]:
        return await self.sem_repo.get_for_year(academic_year_id)

    # --------------------------------------------------------------------------
    # Programs & Specializations
    # --------------------------------------------------------------------------

    async def create_program(self, data: AcademicProgramCreate) -> AcademicProgram:
        # Department must exist
        dept = await self.get_unit(data.department_id)
        if dept.unit_type not in ("DEPARTMENT", "SCHOOL"):
            raise ValidationException("Programs must be anchored to a Department or School.")
        
        existing = await self.prog_repo.get_by_code(data.program_code)
        if existing:
            raise ConflictException(f"Program with code '{data.program_code}' already exists.")
        
        return await self.prog_repo.create(data)

    async def get_program(self, program_id: uuid.UUID) -> AcademicProgram:
        prog = await self.prog_repo.get_by_id(program_id)
        if not prog:
            raise NotFoundException(f"Program with ID '{program_id}' not found.")
        return prog

    async def list_programs_for_department(self, department_id: uuid.UUID) -> Sequence[AcademicProgram]:
        return await self.prog_repo.get_by_department(department_id)

    async def create_specialization(self, data: SpecializationCreate) -> Specialization:
        await self.get_program(data.program_id)
        return await self.spec_repo.create(data)

    # --------------------------------------------------------------------------
    # Courses
    # --------------------------------------------------------------------------

    async def create_course(self, data: CourseCreate) -> Course:
        await self.get_unit(data.department_id)
        existing = await self.course_repo.get_by_code(data.course_code)
        if existing:
            raise ConflictException(f"Course with code '{data.course_code}' already exists.")
        return await self.course_repo.create(data)

    async def get_course(self, course_id: uuid.UUID) -> Course:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundException(f"Course with ID '{course_id}' not found.")
        return course

    async def list_courses_for_department(self, department_id: uuid.UUID) -> Sequence[Course]:
        return await self.course_repo.get_by_department(department_id)

    # --------------------------------------------------------------------------
    # Batches & Sections
    # --------------------------------------------------------------------------

    async def create_batch(self, data: AcademicBatchCreate) -> AcademicBatch:
        await self.get_program(data.program_id)
        if data.graduation_year <= data.admission_year:
            raise ValidationException("Graduation year must be greater than admission year.")
        return await self.batch_repo.create(data)

    async def list_batches_for_program(self, program_id: uuid.UUID) -> Sequence[AcademicBatch]:
        return await self.batch_repo.get_by_program(program_id)

    async def create_section(self, data: SectionCreate) -> Section:
        batch = await self.batch_repo.get_by_id(data.batch_id)
        if not batch:
            raise NotFoundException(f"Academic batch '{data.batch_id}' not found.")
        return await self.sec_repo.create(data)

    async def list_sections_for_batch(self, batch_id: uuid.UUID) -> Sequence[Section]:
        return await self.sec_repo.get_by_batch(batch_id)
