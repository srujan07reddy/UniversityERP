import uuid
from typing import Any, Dict, List, Optional, Sequence, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.students.models import (
    Student,
    StudentAcademicRecord,
    StudentEnrollment,
    StudentLifecycleEvent,
)
from app.domains.students.schemas import (
    StudentAcademicRecordCreate,
    StudentCreate,
    StudentEnrollmentCreate,
    StudentUpdate,
)
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student, StudentCreate, StudentUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Student, session)

    async def get_by_admission_number(self, admission_number: str) -> Optional[Student]:
        query = select(self.model).where(self.model.admission_number == admission_number.strip().upper())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_register_number(self, register_number: str) -> Optional[Student]:
        query = select(self.model).where(self.model.register_number == register_number.strip().upper())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_institutional_email(self, email: str) -> Optional[Student]:
        query = select(self.model).where(self.model.institutional_email == email.strip().lower())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Student]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_with_relations(self, student_id: uuid.UUID) -> Optional[Student]:
        """Fetch complete student dossier including academic records, enrollments, and lifecycle events."""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.academic_records),
                selectinload(self.model.enrollments),
                selectinload(self.model.lifecycle_events),
            )
            .where(self.model.id == student_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_students(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        department_id: Optional[uuid.UUID] = None,
        program_id: Optional[uuid.UUID] = None,
        batch_id: Optional[uuid.UUID] = None,
        section_id: Optional[uuid.UUID] = None,
        student_status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[Sequence[Student], int]:
        """
        List students with optional institutional filtering and text search.
        Returns (items, total_count).
        """
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        filters = []
        if department_id:
            filters.append(self.model.department_id == department_id)
        if program_id:
            filters.append(self.model.program_id == program_id)
        if batch_id:
            filters.append(self.model.batch_id == batch_id)
        if section_id:
            filters.append(self.model.section_id == section_id)
        if student_status:
            filters.append(self.model.student_status == student_status.strip().upper())
        if search:
            search_clean = f"%{search.strip().lower()}%"
            filters.append(
                or_(
                    func.lower(self.model.admission_number).like(search_clean),
                    func.lower(self.model.register_number).like(search_clean),
                    func.lower(self.model.first_name).like(search_clean),
                    func.lower(self.model.last_name).like(search_clean),
                )
            )

        if filters:
            for f in filters:
                query = query.where(f)
                count_query = count_query.where(f)

        total_res = await self.session.execute(count_query)
        total = total_res.scalar() or 0

        query = query.order_by(self.model.admission_number).offset(offset).limit(limit)
        items_res = await self.session.execute(query)
        items = items_res.scalars().all()

        return items, total


class StudentAcademicRecordRepository(BaseRepository[StudentAcademicRecord, StudentAcademicRecordCreate, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(StudentAcademicRecord, session)

    async def get_by_student(self, student_id: uuid.UUID) -> Sequence[StudentAcademicRecord]:
        query = (
            select(self.model)
            .where(self.model.student_id == student_id)
            .order_by(self.model.year_of_passing)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class StudentEnrollmentRepository(BaseRepository[StudentEnrollment, StudentEnrollmentCreate, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(StudentEnrollment, session)

    async def get_by_student(self, student_id: uuid.UUID) -> Sequence[StudentEnrollment]:
        query = (
            select(self.model)
            .where(self.model.student_id == student_id)
            .order_by(self.model.semester_number)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_student_and_semester(
        self, student_id: uuid.UUID, semester_number: int
    ) -> Optional[StudentEnrollment]:
        query = (
            select(self.model)
            .where(
                self.model.student_id == student_id,
                self.model.semester_number == semester_number,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()


class StudentLifecycleEventRepository(BaseRepository[StudentLifecycleEvent, Any, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(StudentLifecycleEvent, session)

    async def get_by_student(self, student_id: uuid.UUID) -> Sequence[StudentLifecycleEvent]:
        query = (
            select(self.model)
            .where(self.model.student_id == student_id)
            .order_by(self.model.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()
