import uuid
from typing import Any, Optional, Sequence, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.staff.models import (
    Staff,
    StaffDepartmentAffiliation,
    StaffExperience,
    StaffLifecycleEvent,
    StaffQualification,
)
from app.domains.staff.schemas import (
    StaffCreate,
    StaffDepartmentAffiliationCreate,
    StaffExperienceCreate,
    StaffQualificationCreate,
    StaffUpdate,
)
from app.repositories.base import BaseRepository


class StaffRepository(BaseRepository[Staff, StaffCreate, StaffUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Staff, session)

    async def get_by_staff_id(self, staff_id: str) -> Optional[Staff]:
        query = select(self.model).where(self.model.staff_id == staff_id.strip().upper())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_biometric_id(self, biometric_id: str) -> Optional[Staff]:
        query = select(self.model).where(self.model.biometric_id == biometric_id.strip().upper())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_institutional_email(self, email: str) -> Optional[Staff]:
        query = select(self.model).where(self.model.institutional_email == email.strip().lower())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Staff]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_with_relations(self, staff_id: uuid.UUID) -> Optional[Staff]:
        """Fetch complete staff member dossier including qualifications, experience, and lifecycle events."""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.qualifications),
                selectinload(self.model.experience_records),
                selectinload(self.model.department_affiliations),
                selectinload(self.model.lifecycle_events),
            )
            .where(self.model.id == staff_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_staff(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        department_id: Optional[uuid.UUID] = None,
        school_id: Optional[uuid.UUID] = None,
        staff_type: Optional[str] = None,
        employment_status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[Sequence[Staff], int]:
        """
        List staff members with optional organizational filtering and text search.
        Returns (items, total_count).
        """
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        filters = []
        if department_id:
            filters.append(self.model.department_id == department_id)
        if school_id:
            filters.append(self.model.school_id == school_id)
        if staff_type:
            filters.append(self.model.staff_type == staff_type.strip().upper())
        if employment_status:
            filters.append(self.model.employment_status == employment_status.strip().upper())
        if search:
            search_clean = f"%{search.strip().lower()}%"
            filters.append(
                or_(
                    func.lower(self.model.staff_id).like(search_clean),
                    func.lower(self.model.first_name).like(search_clean),
                    func.lower(self.model.last_name).like(search_clean),
                    func.lower(self.model.designation).like(search_clean),
                )
            )

        if filters:
            for f in filters:
                query = query.where(f)
                count_query = count_query.where(f)

        total_res = await self.session.execute(count_query)
        total = total_res.scalar() or 0

        query = query.order_by(self.model.staff_id).offset(offset).limit(limit)
        items_res = await self.session.execute(query)
        items = items_res.scalars().all()

        return items, total


class StaffQualificationRepository(BaseRepository[StaffQualification, StaffQualificationCreate, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(StaffQualification, session)

    async def get_by_staff(self, staff_id: uuid.UUID) -> Sequence[StaffQualification]:
        query = (
            select(self.model)
            .where(self.model.staff_id == staff_id)
            .order_by(self.model.year_of_passing.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class StaffExperienceRepository(BaseRepository[StaffExperience, StaffExperienceCreate, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(StaffExperience, session)

    async def get_by_staff(self, staff_id: uuid.UUID) -> Sequence[StaffExperience]:
        query = (
            select(self.model)
            .where(self.model.staff_id == staff_id)
            .order_by(self.model.start_date.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class StaffLifecycleEventRepository(BaseRepository[StaffLifecycleEvent, Any, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(StaffLifecycleEvent, session)

    async def get_by_staff(self, staff_id: uuid.UUID) -> Sequence[StaffLifecycleEvent]:
        query = (
            select(self.model)
            .where(self.model.staff_id == staff_id)
            .order_by(self.model.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class StaffDepartmentAffiliationRepository(BaseRepository[StaffDepartmentAffiliation, StaffDepartmentAffiliationCreate, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(StaffDepartmentAffiliation, session)

    async def get_for_staff(self, staff_id: uuid.UUID) -> Sequence[StaffDepartmentAffiliation]:
        query = (
            select(self.model)
            .where(self.model.staff_id == staff_id)
            .order_by(self.model.start_date.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_staff_and_department(
        self, staff_id: uuid.UUID, department_id: uuid.UUID, affiliation_type: str
    ) -> Optional[StaffDepartmentAffiliation]:
        query = select(self.model).where(
            self.model.staff_id == staff_id,
            self.model.department_id == department_id,
            self.model.affiliation_type == affiliation_type.strip().upper(),
        )
        result = await self.session.execute(query)
        return result.scalars().first()
