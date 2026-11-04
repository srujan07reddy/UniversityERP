import uuid
from typing import Any, List, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.platform.organization.schemas import (
    AcademicBatchCreate,
    AcademicBatchUpdate,
    AcademicProgramCreate,
    AcademicProgramUpdate,
    AcademicYearCreate,
    AcademicYearUpdate,
    CourseCreate,
    CourseUpdate,
    OrganizationalRelationshipCreate,
    OrganizationalUnitCreate,
    OrganizationalUnitUpdate,
    SectionCreate,
    SectionUpdate,
    SemesterCreate,
    SemesterUpdate,
    SpecializationCreate,
    UniversityCreate,
    UniversityUpdate,
)
from app.repositories.base import BaseRepository


class UniversityRepository(BaseRepository[University, UniversityCreate, UniversityUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(University, session)

    async def get_by_code(self, code: str) -> Optional[University]:
        query = select(self.model).where(self.model.code == code)
        result = await self.session.execute(query)
        return result.scalars().first()


class OrganizationalUnitRepository(BaseRepository[OrganizationalUnit, OrganizationalUnitCreate, OrganizationalUnitUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(OrganizationalUnit, session)

    async def get_by_code(self, code: str) -> Optional[OrganizationalUnit]:
        query = select(self.model).where(self.model.code == code)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_root_units(self, university_id: uuid.UUID) -> Sequence[OrganizationalUnit]:
        query = (
            select(self.model)
            .where(self.model.university_id == university_id, self.model.parent_unit_id.is_(None))
            .order_by(self.model.name)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_children(self, parent_unit_id: uuid.UUID) -> Sequence[OrganizationalUnit]:
        query = (
            select(self.model)
            .where(self.model.parent_unit_id == parent_unit_id)
            .order_by(self.model.name)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_type(self, university_id: uuid.UUID, unit_type: str) -> Sequence[OrganizationalUnit]:
        query = (
            select(self.model)
            .where(self.model.university_id == university_id, self.model.unit_type == unit_type)
            .order_by(self.model.name)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class OrganizationalRelationshipRepository(BaseRepository[OrganizationalRelationship, OrganizationalRelationshipCreate, Any]):  # type: ignore
    def __init__(self, session: AsyncSession):
        super().__init__(OrganizationalRelationship, session)

    async def get_for_unit(self, unit_id: uuid.UUID) -> Sequence[OrganizationalRelationship]:
        query = (
            select(self.model)
            .where((self.model.source_unit_id == unit_id) | (self.model.target_unit_id == unit_id))
            .order_by(self.model.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class AcademicYearRepository(BaseRepository[AcademicYear, AcademicYearCreate, AcademicYearUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(AcademicYear, session)

    async def get_current(self, university_id: uuid.UUID) -> Optional[AcademicYear]:
        query = (
            select(self.model)
            .where(self.model.university_id == university_id, self.model.is_current.is_(True))
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_name(self, university_id: uuid.UUID, year_name: str) -> Optional[AcademicYear]:
        query = (
            select(self.model)
            .where(self.model.university_id == university_id, self.model.year_name == year_name)
        )
        result = await self.session.execute(query)
        return result.scalars().first()


class SemesterRepository(BaseRepository[Semester, SemesterCreate, SemesterUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Semester, session)

    async def get_by_year_and_number(self, academic_year_id: uuid.UUID, semester_number: int) -> Optional[Semester]:
        query = (
            select(self.model)
            .where(self.model.academic_year_id == academic_year_id, self.model.semester_number == semester_number)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_for_year(self, academic_year_id: uuid.UUID) -> Sequence[Semester]:
        query = (
            select(self.model)
            .where(self.model.academic_year_id == academic_year_id)
            .order_by(self.model.semester_number)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class AcademicProgramRepository(BaseRepository[AcademicProgram, AcademicProgramCreate, AcademicProgramUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(AcademicProgram, session)

    async def get_by_code(self, code: str) -> Optional[AcademicProgram]:
        query = select(self.model).where(self.model.program_code == code)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_department(self, department_id: uuid.UUID) -> Sequence[AcademicProgram]:
        query = (
            select(self.model)
            .where(self.model.department_id == department_id)
            .order_by(self.model.program_name)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class SpecializationRepository(BaseRepository[Specialization, SpecializationCreate, Any]):  # type: ignore
    def __init__(self, session: AsyncSession):
        super().__init__(Specialization, session)

    async def get_by_program(self, program_id: uuid.UUID) -> Sequence[Specialization]:
        query = (
            select(self.model)
            .where(self.model.program_id == program_id)
            .order_by(self.model.specialization_name)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class CourseRepository(BaseRepository[Course, CourseCreate, CourseUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    async def get_by_code(self, code: str) -> Optional[Course]:
        query = select(self.model).where(self.model.course_code == code)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_department(self, department_id: uuid.UUID) -> Sequence[Course]:
        query = (
            select(self.model)
            .where(self.model.department_id == department_id)
            .order_by(self.model.course_code)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class AcademicBatchRepository(BaseRepository[AcademicBatch, AcademicBatchCreate, AcademicBatchUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(AcademicBatch, session)

    async def get_by_program(self, program_id: uuid.UUID) -> Sequence[AcademicBatch]:
        query = (
            select(self.model)
            .where(self.model.program_id == program_id)
            .order_by(self.model.admission_year.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class SectionRepository(BaseRepository[Section, SectionCreate, SectionUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Section, session)

    async def get_by_batch(self, batch_id: uuid.UUID) -> Sequence[Section]:
        query = (
            select(self.model)
            .where(self.model.batch_id == batch_id)
            .order_by(self.model.section_name)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
