import uuid
from datetime import date
from typing import Any, Dict, List, Optional, Sequence, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.domains.staff.models import (
    Staff,
    StaffDepartmentAffiliation,
    StaffExperience,
    StaffLifecycleEvent,
    StaffQualification,
)
from app.domains.staff.repositories import (
    StaffDepartmentAffiliationRepository,
    StaffExperienceRepository,
    StaffLifecycleEventRepository,
    StaffQualificationRepository,
    StaffRepository,
)
from app.domains.staff.schemas import (
    StaffCreate,
    StaffDepartmentAffiliationCreate,
    StaffDepartmentTransfer,
    StaffDesignationUpdate,
    StaffExperienceCreate,
    StaffQualificationCreate,
    StaffStatusUpdate,
    StaffUpdate,
)
from app.platform.organization.models import OrganizationalUnit


VALID_STAFF_STATUSES = {
    "ACTIVE",
    "PROBATION",
    "ON_LEAVE",
    "SUSPENDED",
    "RESIGNED",
    "RETIRED",
    "TERMINATED",
    "RELIEVED",
}

VALID_STAFF_TYPES = {
    "TEACHING",
    "NON_TEACHING",
    "ADMINISTRATIVE",
    "TECHNICAL",
    "EXECUTIVE",
    "SUPPORT",
}


class StaffService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.staff_repo = StaffRepository(session)
        self.qual_repo = StaffQualificationRepository(session)
        self.exp_repo = StaffExperienceRepository(session)
        self.event_repo = StaffLifecycleEventRepository(session)
        self.affiliation_repo = StaffDepartmentAffiliationRepository(session)

    async def create_staff(self, data: StaffCreate) -> Staff:
        """
        Appoint and register a new institutional staff member.
        Enforces unique staff ID, biometric ID, and institutional email,
        validates department and school hierarchy, and records initial appointment audit event.
        """
        # 1. Uniqueness Checks
        norm_staff_id = data.staff_id.strip().upper()
        existing_staff = await self.staff_repo.get_by_staff_id(norm_staff_id)
        if existing_staff:
            raise ConflictException(f"Staff member with Staff ID '{norm_staff_id}' already exists.")

        if data.biometric_id:
            norm_bio = data.biometric_id.strip().upper()
            existing_bio = await self.staff_repo.get_by_biometric_id(norm_bio)
            if existing_bio:
                raise ConflictException(f"Biometric ID '{norm_bio}' is already assigned.")

        if data.institutional_email:
            norm_email = str(data.institutional_email).strip().lower()
            existing_email = await self.staff_repo.get_by_institutional_email(norm_email)
            if existing_email:
                raise ConflictException(f"Institutional email '{norm_email}' is already in use.")

        # 2. Institutional Hierarchy Validation
        dept = await self.session.get(OrganizationalUnit, data.department_id)
        if not dept:
            raise NotFoundException(f"Department unit with ID {data.department_id} not found.")

        if data.school_id:
            school = await self.session.get(OrganizationalUnit, data.school_id)
            if not school:
                raise NotFoundException(f"School unit with ID {data.school_id} not found.")

        # 3. Create Staff Entity
        staff_dict = data.model_dump(
            exclude={"initial_qualifications", "initial_experience"}, exclude_unset=True
        )
        staff_dict["staff_id"] = norm_staff_id
        if data.biometric_id:
            staff_dict["biometric_id"] = data.biometric_id.strip().upper()
        if data.institutional_email:
            staff_dict["institutional_email"] = str(data.institutional_email).strip().lower()
        if data.personal_email:
            staff_dict["personal_email"] = str(data.personal_email).strip().lower()
        staff_dict["staff_type"] = data.staff_type.strip().upper()
        staff_dict["employment_status"] = data.employment_status.strip().upper()

        staff = await self.staff_repo.create(staff_dict)

        # 4. Create Initial Qualifications if provided
        if data.initial_qualifications:
            for q_in in data.initial_qualifications:
                q_dict = q_in.model_dump()
                q_dict["staff_id"] = staff.id
                await self.qual_repo.create(q_dict)

        # 5. Create Initial Experience if provided
        if data.initial_experience:
            for exp_in in data.initial_experience:
                exp_dict = exp_in.model_dump()
                exp_dict["staff_id"] = staff.id
                await self.exp_repo.create(exp_dict)

        # 6. Record Initial Appointment Lifecycle Event
        await self.event_repo.create({
            "staff_id": staff.id,
            "event_type": "APPOINTMENT",
            "previous_status": None,
            "new_status": staff.employment_status,
            "reason": f"Official appointment as {staff.designation}",
            "metadata_json": {
                "staff_id": norm_staff_id,
                "staff_type": staff.staff_type,
                "designation": staff.designation,
                "department_id": str(staff.department_id),
                "date_of_joining": staff.date_of_joining.isoformat(),
            },
        })

        await self.session.flush()
        fresh = await self.staff_repo.get_with_relations(staff.id)
        return fresh or staff

    async def get_staff(self, staff_id: uuid.UUID) -> Staff:
        staff = await self.staff_repo.get_by_id(staff_id)
        if not staff:
            raise NotFoundException(f"Staff member with ID {staff_id} not found.")
        return staff

    async def get_staff_detail(self, staff_id: uuid.UUID) -> Staff:
        staff = await self.staff_repo.get_with_relations(staff_id)
        if not staff:
            raise NotFoundException(f"Staff member with ID {staff_id} not found.")
        return staff

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
        return await self.staff_repo.list_staff(
            offset=offset,
            limit=limit,
            department_id=department_id,
            school_id=school_id,
            staff_type=staff_type,
            employment_status=employment_status,
            search=search,
        )

    async def update_staff(self, staff_id: uuid.UUID, data: StaffUpdate) -> Staff:
        staff = await self.get_staff(staff_id)

        update_dict = data.model_dump(exclude_unset=True)

        if "biometric_id" in update_dict and update_dict["biometric_id"]:
            norm_bio = update_dict["biometric_id"].strip().upper()
            existing = await self.staff_repo.get_by_biometric_id(norm_bio)
            if existing and existing.id != staff_id:
                raise ConflictException(f"Biometric ID '{norm_bio}' is already assigned to another staff member.")
            update_dict["biometric_id"] = norm_bio

        if "institutional_email" in update_dict and update_dict["institutional_email"]:
            norm_email = str(update_dict["institutional_email"]).strip().lower()
            existing = await self.staff_repo.get_by_institutional_email(norm_email)
            if existing and existing.id != staff_id:
                raise ConflictException(f"Email '{norm_email}' is already assigned to another staff member.")
            update_dict["institutional_email"] = norm_email

        if "staff_type" in update_dict and update_dict["staff_type"]:
            update_dict["staff_type"] = update_dict["staff_type"].strip().upper()

        updated = await self.staff_repo.update(db_obj=staff, obj_in=update_dict)
        await self.session.flush()
        fresh = await self.staff_repo.get_by_id(updated.id)
        return fresh or updated

    async def update_staff_status(self, staff_id: uuid.UUID, data: StaffStatusUpdate) -> Staff:
        staff = await self.get_staff(staff_id)
        new_status = data.new_status.strip().upper()

        if new_status not in VALID_STAFF_STATUSES:
            raise BadRequestException(
                f"Invalid status '{new_status}'. Allowed statuses: {', '.join(sorted(VALID_STAFF_STATUSES))}"
            )

        if staff.employment_status == new_status:
            return staff

        prev_status = staff.employment_status
        today = date.today()

        payload: Dict[str, Any] = {
            "employment_status": new_status,
            "status_change_date": today,
            "status_reason": data.reason,
        }
        if data.date_of_relieving:
            payload["date_of_relieving"] = data.date_of_relieving
            payload["relieving_reason"] = data.reason

        await self.staff_repo.update(db_obj=staff, obj_in=payload)

        # Audit Event
        await self.event_repo.create({
            "staff_id": staff.id,
            "event_type": "STATUS_CHANGE",
            "previous_status": prev_status,
            "new_status": new_status,
            "reason": data.reason,
            "performed_by_id": data.performed_by_id,
            "metadata_json": {
                "date": today.isoformat(),
                "relieving_date": data.date_of_relieving.isoformat() if data.date_of_relieving else None,
                "reason": data.reason,
            },
        })

        await self.session.flush()
        fresh = await self.staff_repo.get_by_id(staff.id)
        return fresh or staff

    async def update_designation(self, staff_id: uuid.UUID, data: StaffDesignationUpdate) -> Staff:
        staff = await self.get_staff(staff_id)
        old_desig = staff.designation
        new_desig = data.new_designation.strip()

        await self.staff_repo.update(db_obj=staff, obj_in={"designation": new_desig})

        # Audit Event
        await self.event_repo.create({
            "staff_id": staff.id,
            "event_type": "DESIGNATION_CHANGE",
            "previous_status": staff.employment_status,
            "new_status": staff.employment_status,
            "reason": data.reason or f"Redesignation from {old_desig} to {new_desig}",
            "metadata_json": {
                "old_designation": old_desig,
                "new_designation": new_desig,
                "effective_date": (data.effective_date or date.today()).isoformat(),
            },
        })

        await self.session.flush()
        fresh = await self.staff_repo.get_by_id(staff.id)
        return fresh or staff

    async def transfer_department(self, staff_id: uuid.UUID, data: StaffDepartmentTransfer) -> Staff:
        staff = await self.get_staff(staff_id)

        target_dept = await self.session.get(OrganizationalUnit, data.new_department_id)
        if not target_dept:
            raise NotFoundException(f"Target department {data.new_department_id} not found.")

        if data.new_school_id:
            target_school = await self.session.get(OrganizationalUnit, data.new_school_id)
            if not target_school:
                raise NotFoundException(f"Target school {data.new_school_id} not found.")

        old_dept_id = staff.department_id
        old_school_id = staff.school_id

        await self.staff_repo.update(
            db_obj=staff,
            obj_in={
                "department_id": data.new_department_id,
                "school_id": data.new_school_id,
            },
        )

        # Audit Event
        await self.event_repo.create({
            "staff_id": staff.id,
            "event_type": "DEPARTMENT_TRANSFER",
            "previous_status": staff.employment_status,
            "new_status": staff.employment_status,
            "reason": data.reason or "Departmental transfer order",
            "metadata_json": {
                "from_department_id": str(old_dept_id),
                "to_department_id": str(data.new_department_id),
                "from_school_id": str(old_school_id) if old_school_id else None,
                "to_school_id": str(data.new_school_id) if data.new_school_id else None,
            },
        })

        await self.session.flush()
        fresh = await self.staff_repo.get_by_id(staff.id)
        return fresh or staff

    async def add_qualification(
        self, staff_id: uuid.UUID, data: StaffQualificationCreate
    ) -> StaffQualification:
        staff = await self.get_staff(staff_id)
        q_dict = data.model_dump()
        q_dict["staff_id"] = staff.id
        record = await self.qual_repo.create(q_dict)
        await self.session.flush()
        return record

    async def add_experience(
        self, staff_id: uuid.UUID, data: StaffExperienceCreate
    ) -> StaffExperience:
        staff = await self.get_staff(staff_id)
        exp_dict = data.model_dump()
        exp_dict["staff_id"] = staff.id
        record = await self.exp_repo.create(exp_dict)
        await self.session.flush()
        return record

    async def add_department_affiliation(
        self, staff_id: uuid.UUID, data: StaffDepartmentAffiliationCreate
    ) -> StaffDepartmentAffiliation:
        staff = await self.get_staff(staff_id)
        dept = await self.session.get(OrganizationalUnit, data.department_id)
        if not dept:
            raise NotFoundException(f"Department unit with ID {data.department_id} not found.")

        norm_type = data.affiliation_type.strip().upper()
        existing = await self.affiliation_repo.get_by_staff_and_department(
            staff_id, data.department_id, norm_type
        )
        if existing and existing.is_active:
            raise ConflictException(
                f"Staff member already has an active '{norm_type}' affiliation with department '{dept.name}'."
            )

        aff_dict = data.model_dump()
        aff_dict["staff_id"] = staff.id
        aff_dict["affiliation_type"] = norm_type
        affiliation = await self.affiliation_repo.create(aff_dict)

        # Audit Event
        await self.event_repo.create({
            "staff_id": staff.id,
            "event_type": "AFFILIATION_ADDED",
            "previous_status": staff.employment_status,
            "new_status": staff.employment_status,
            "reason": f"Added {norm_type} affiliation with {dept.name}",
            "metadata_json": {
                "department_id": str(dept.id),
                "department_name": dept.name,
                "affiliation_type": norm_type,
                "role_title": data.role_title,
            },
        })

        await self.session.flush()
        return affiliation

    async def list_department_affiliations(
        self, staff_id: uuid.UUID
    ) -> Sequence[StaffDepartmentAffiliation]:
        await self.get_staff(staff_id)
        return await self.affiliation_repo.get_for_staff(staff_id)

    async def remove_department_affiliation(self, affiliation_id: uuid.UUID) -> None:
        affiliation = await self.affiliation_repo.get_by_id(affiliation_id)
        if not affiliation:
            raise NotFoundException(f"Affiliation record {affiliation_id} not found.")

        staff_id = affiliation.staff_id
        await self.session.delete(affiliation)

        await self.event_repo.create({
            "staff_id": staff_id,
            "event_type": "AFFILIATION_REMOVED",
            "reason": "Department affiliation terminated",
            "metadata_json": {"affiliation_id": str(affiliation_id)},
        })

        await self.session.flush()

