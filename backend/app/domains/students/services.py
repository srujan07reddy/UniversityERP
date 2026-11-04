import uuid
from datetime import date
from typing import Any, Dict, List, Optional, Sequence, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.domains.students.models import (
    Student,
    StudentAcademicRecord,
    StudentEnrollment,
    StudentLifecycleEvent,
)
from app.domains.students.repositories import (
    StudentAcademicRecordRepository,
    StudentEnrollmentRepository,
    StudentLifecycleEventRepository,
    StudentRepository,
)
from app.domains.students.schemas import (
    StudentAcademicRecordCreate,
    StudentCreate,
    StudentEnrollmentCreate,
    StudentSectionAssign,
    StudentStatusUpdate,
    StudentUpdate,
)
from app.platform.organization.models import (
    AcademicBatch,
    AcademicProgram,
    AcademicYear,
    OrganizationalUnit,
    Section,
    Semester,
)


VALID_STUDENT_STATUSES = {
    "ADMITTED",
    "ACTIVE",
    "ON_LEAVE",
    "SUSPENDED",
    "DISCONTINUED",
    "ALUMNI",
    "WITHDRAWN",
}


class StudentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.student_repo = StudentRepository(session)
        self.record_repo = StudentAcademicRecordRepository(session)
        self.enrollment_repo = StudentEnrollmentRepository(session)
        self.event_repo = StudentLifecycleEventRepository(session)

    async def create_student(self, data: StudentCreate) -> Student:
        """
        Admit and register a new institutional student.
        Validates academic associations, ensures unique admission number,
        and logs the initial admission lifecycle event.
        """
        # 1. Uniqueness Checks
        norm_admission = data.admission_number.strip().upper()
        existing_adm = await self.student_repo.get_by_admission_number(norm_admission)
        if existing_adm:
            raise ConflictException(f"Student with admission number '{norm_admission}' already exists.")

        if data.register_number:
            norm_reg = data.register_number.strip().upper()
            existing_reg = await self.student_repo.get_by_register_number(norm_reg)
            if existing_reg:
                raise ConflictException(f"Student with register number '{norm_reg}' already exists.")

        if data.institutional_email:
            norm_email = str(data.institutional_email).strip().lower()
            existing_email = await self.student_repo.get_by_institutional_email(norm_email)
            if existing_email:
                raise ConflictException(f"Student with institutional email '{norm_email}' already exists.")

        # 2. Institutional Hierarchy Validation
        dept = await self.session.get(OrganizationalUnit, data.department_id)
        if not dept:
            raise NotFoundException(f"Department unit with ID {data.department_id} not found.")

        prog = await self.session.get(AcademicProgram, data.program_id)
        if not prog:
            raise NotFoundException(f"Academic Program with ID {data.program_id} not found.")

        if data.batch_id:
            batch = await self.session.get(AcademicBatch, data.batch_id)
            if not batch:
                raise NotFoundException(f"Academic Batch with ID {data.batch_id} not found.")

        if data.section_id:
            sec = await self.session.get(Section, data.section_id)
            if not sec:
                raise NotFoundException(f"Section with ID {data.section_id} not found.")

        # 3. Create Student Entity
        student_dict = data.model_dump(exclude={"initial_academic_records"}, exclude_unset=True)
        student_dict["admission_number"] = norm_admission
        if data.register_number:
            student_dict["register_number"] = data.register_number.strip().upper()
        if data.institutional_email:
            student_dict["institutional_email"] = str(data.institutional_email).strip().lower()
        if data.personal_email:
            student_dict["personal_email"] = str(data.personal_email).strip().lower()
        student_dict["student_status"] = data.student_status.strip().upper()

        student = await self.student_repo.create(student_dict)

        # 4. Create Initial Academic Records if provided
        if data.initial_academic_records:
            for rec_in in data.initial_academic_records:
                rec_dict = rec_in.model_dump()
                rec_dict["student_id"] = student.id
                await self.record_repo.create(rec_dict)

        # 5. Record Initial Admission Lifecycle Event
        await self.event_repo.create({
            "student_id": student.id,
            "event_type": "ADMISSION",
            "previous_status": None,
            "new_status": student.student_status,
            "reason": "Initial institutional admission registration",
            "metadata_json": {
                "admission_number": norm_admission,
                "admission_category": student.admission_category,
                "program_id": str(student.program_id),
                "department_id": str(student.department_id),
            },
        })

        await self.session.flush()
        fresh = await self.student_repo.get_with_relations(student.id)
        return fresh or student

    async def get_student(self, student_id: uuid.UUID) -> Student:
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundException(f"Student with ID {student_id} not found.")
        return student

    async def get_student_detail(self, student_id: uuid.UUID) -> Student:
        student = await self.student_repo.get_with_relations(student_id)
        if not student:
            raise NotFoundException(f"Student with ID {student_id} not found.")
        return student

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
        return await self.student_repo.list_students(
            offset=offset,
            limit=limit,
            department_id=department_id,
            program_id=program_id,
            batch_id=batch_id,
            section_id=section_id,
            student_status=student_status,
            search=search,
        )

    async def update_student(self, student_id: uuid.UUID, data: StudentUpdate) -> Student:
        student = await self.get_student(student_id)

        update_dict = data.model_dump(exclude_unset=True)

        if "register_number" in update_dict and update_dict["register_number"]:
            norm_reg = update_dict["register_number"].strip().upper()
            existing = await self.student_repo.get_by_register_number(norm_reg)
            if existing and existing.id != student_id:
                raise ConflictException(f"Register number '{norm_reg}' is already assigned to another student.")
            update_dict["register_number"] = norm_reg

        if "institutional_email" in update_dict and update_dict["institutional_email"]:
            norm_email = str(update_dict["institutional_email"]).strip().lower()
            existing = await self.student_repo.get_by_institutional_email(norm_email)
            if existing and existing.id != student_id:
                raise ConflictException(f"Email '{norm_email}' is already assigned to another student.")
            update_dict["institutional_email"] = norm_email

        if "department_id" in update_dict and update_dict["department_id"]:
            dept = await self.session.get(OrganizationalUnit, update_dict["department_id"])
            if not dept:
                raise NotFoundException(f"Department ID {update_dict['department_id']} not found.")

        if "program_id" in update_dict and update_dict["program_id"]:
            prog = await self.session.get(AcademicProgram, update_dict["program_id"])
            if not prog:
                raise NotFoundException(f"Program ID {update_dict['program_id']} not found.")

        if "batch_id" in update_dict and update_dict["batch_id"]:
            batch = await self.session.get(AcademicBatch, update_dict["batch_id"])
            if not batch:
                raise NotFoundException(f"Batch ID {update_dict['batch_id']} not found.")

        if "section_id" in update_dict and update_dict["section_id"]:
            sec = await self.session.get(Section, update_dict["section_id"])
            if not sec:
                raise NotFoundException(f"Section ID {update_dict['section_id']} not found.")

        updated = await self.student_repo.update(db_obj=student, obj_in=update_dict)
        await self.session.flush()
        fresh = await self.student_repo.get_by_id(updated.id)
        return fresh or updated

    async def update_student_status(
        self, student_id: uuid.UUID, data: StudentStatusUpdate
    ) -> Student:
        student = await self.get_student(student_id)
        new_status = data.new_status.strip().upper()

        if new_status not in VALID_STUDENT_STATUSES:
            raise BadRequestException(
                f"Invalid status '{new_status}'. Allowed statuses: {', '.join(sorted(VALID_STUDENT_STATUSES))}"
            )

        if student.student_status == new_status:
            return student

        prev_status = student.student_status
        today = date.today()

        await self.student_repo.update(
            db_obj=student,
            obj_in={
                "student_status": new_status,
                "status_change_date": today,
                "status_reason": data.reason,
            },
        )

        # Audit Event
        await self.event_repo.create({
            "student_id": student.id,
            "event_type": "STATUS_CHANGE",
            "previous_status": prev_status,
            "new_status": new_status,
            "reason": data.reason,
            "performed_by_id": data.performed_by_id,
            "metadata_json": {
                "date": today.isoformat(),
                "reason": data.reason,
            },
        })

        await self.session.flush()
        fresh = await self.student_repo.get_by_id(student.id)
        return fresh or student

    async def assign_section(
        self, student_id: uuid.UUID, data: StudentSectionAssign
    ) -> Student:
        student = await self.get_student(student_id)

        if data.batch_id:
            batch = await self.session.get(AcademicBatch, data.batch_id)
            if not batch:
                raise NotFoundException(f"Batch ID {data.batch_id} not found.")

        if data.section_id:
            sec = await self.session.get(Section, data.section_id)
            if not sec:
                raise NotFoundException(f"Section ID {data.section_id} not found.")

        update_payload: Dict[str, Any] = {}
        if data.batch_id is not None:
            update_payload["batch_id"] = data.batch_id
        if data.section_id is not None:
            update_payload["section_id"] = data.section_id
        if data.roll_number is not None:
            update_payload["roll_number"] = data.roll_number.strip().upper()

        await self.student_repo.update(db_obj=student, obj_in=update_payload)

        # Audit Event
        await self.event_repo.create({
            "student_id": student.id,
            "event_type": "SECTION_ASSIGNED",
            "previous_status": student.student_status,
            "new_status": student.student_status,
            "reason": data.reason or "Assigned to batch and section",
            "metadata_json": {
                "batch_id": str(data.batch_id) if data.batch_id else None,
                "section_id": str(data.section_id) if data.section_id else None,
                "roll_number": data.roll_number,
            },
        })

        await self.session.flush()
        fresh = await self.student_repo.get_by_id(student.id)
        return fresh or student

    async def add_academic_record(
        self, student_id: uuid.UUID, data: StudentAcademicRecordCreate
    ) -> StudentAcademicRecord:
        student = await self.get_student(student_id)
        rec_data = data.model_dump()
        rec_data["student_id"] = student.id
        record = await self.record_repo.create(rec_data)
        await self.session.flush()
        return record

    async def create_enrollment(
        self, student_id: uuid.UUID, data: StudentEnrollmentCreate
    ) -> StudentEnrollment:
        student = await self.get_student(student_id)

        # Verify academic year
        ay = await self.session.get(AcademicYear, data.academic_year_id)
        if not ay:
            raise NotFoundException(f"Academic Year ID {data.academic_year_id} not found.")

        # Verify semester if provided
        if data.semester_id:
            sem = await self.session.get(Semester, data.semester_id)
            if not sem:
                raise NotFoundException(f"Semester ID {data.semester_id} not found.")

        # Verify program
        prog = await self.session.get(AcademicProgram, data.program_id)
        if not prog:
            raise NotFoundException(f"Program ID {data.program_id} not found.")

        existing = await self.enrollment_repo.get_by_student_and_semester(
            student_id, data.semester_number
        )
        if existing:
            raise ConflictException(
                f"Student already has an enrollment for semester {data.semester_number}."
            )

        enrollment_dict = data.model_dump()
        enrollment_dict["student_id"] = student.id
        enrollment = await self.enrollment_repo.create(enrollment_dict)

        # Advance current_semester if higher
        if data.semester_number > student.current_semester:
            await self.student_repo.update(
                db_obj=student,
                obj_in={"current_semester": data.semester_number},
            )

        # Audit Event
        await self.event_repo.create({
            "student_id": student.id,
            "event_type": "ENROLLMENT",
            "previous_status": student.student_status,
            "new_status": student.student_status,
            "reason": f"Enrolled into semester {data.semester_number}",
            "metadata_json": {
                "semester_number": data.semester_number,
                "academic_year_id": str(data.academic_year_id),
                "enrollment_status": data.enrollment_status,
            },
        })

        await self.session.flush()
        return enrollment
