import uuid
from datetime import date
from typing import Any, Dict, List, Optional
from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditBaseModel


# ==============================================================================
# 1. Student Master Entity
# ==============================================================================

class Student(AuditBaseModel):
    """
    Student Institutional Identity.
    Maintains official student identity, academic enrollment associations,
    and profile data. Remains strictly decoupled from authentication credentials.
    """
    __tablename__ = "students"

    # Optional linkage to central User account (credential authentication handled separately)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
    )

    # Core Institutional Identifiers
    admission_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    register_number: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    roll_number: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)

    # Personal and Demographic Details
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)  # MALE, FEMALE, OTHER
    blood_group: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    nationality: Mapped[str] = mapped_column(String(50), default="Indian", nullable=False)
    religion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    community: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # OC, BC, MBC, SC, ST
    caste: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    aadhar_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Contact & Communication
    personal_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    institutional_email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emergency_contact_relationship: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    permanent_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Parent & Guardian Details
    father_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    father_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    father_occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mother_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mother_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mother_occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    guardian_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    guardian_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Institutional Academic Associations
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizational_units.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_programs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_batches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    section_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Student Lifecycle State
    admission_date: Mapped[date] = mapped_column(Date, nullable=False)
    admission_category: Mapped[str] = mapped_column(String(50), default="REGULAR", nullable=False)
    # Categories: REGULAR, MANAGEMENT, GOVT_QUOTA, LATERAL_ENTRY, NRI, TRANSFER
    current_semester: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    student_status: Mapped[str] = mapped_column(String(50), default="ADMITTED", nullable=False, index=True)
    # Statuses: ADMITTED, ACTIVE, ON_LEAVE, SUSPENDED, DISCONTINUED, ALUMNI, WITHDRAWN
    status_change_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Flexible metadata
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship(  # type: ignore[name-defined]
        "User",
        foreign_keys=[user_id],
        back_populates="student",
    )
    department: Mapped["OrganizationalUnit"] = relationship(foreign_keys=[department_id])  # type: ignore[name-defined]
    program: Mapped["AcademicProgram"] = relationship(foreign_keys=[program_id])  # type: ignore[name-defined]
    batch: Mapped[Optional["AcademicBatch"]] = relationship(foreign_keys=[batch_id])  # type: ignore[name-defined]
    section: Mapped[Optional["Section"]] = relationship(foreign_keys=[section_id])  # type: ignore[name-defined]

    academic_records: Mapped[List["StudentAcademicRecord"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        order_by="StudentAcademicRecord.year_of_passing",
    )
    enrollments: Mapped[List["StudentEnrollment"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        order_by="StudentEnrollment.semester_number",
    )
    lifecycle_events: Mapped[List["StudentLifecycleEvent"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        order_by="StudentLifecycleEvent.created_at.desc()",
    )


# ==============================================================================
# 2. Previous Academic Records
# ==============================================================================

class StudentAcademicRecord(AuditBaseModel):
    """
    Prior educational history (10th, 12th/HSC, Diplomas, UG degrees)
    submitted during admission for eligibility verification and archival.
    """
    __tablename__ = "student_academic_records"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    qualification: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g., "Secondary (10th)", "Higher Secondary (12th)", "Diploma", "Undergraduate"
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    board_or_university: Mapped[str] = mapped_column(String(255), nullable=False)
    year_of_passing: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage_or_cgpa: Mapped[str] = mapped_column(String(50), nullable=False)
    register_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    stream_or_specialization: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="academic_records")


# ==============================================================================
# 3. Student Academic Enrollments (Per Semester / Term)
# ==============================================================================

class StudentEnrollment(AuditBaseModel):
    """
    Academic enrollment registration history tracking student progression
    through semesters, batches, and sections across academic years.
    """
    __tablename__ = "student_enrollments"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    semester_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("semesters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_programs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_batches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    section_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    semester_number: Mapped[int] = mapped_column(Integer, nullable=False)
    enrollment_date: Mapped[date] = mapped_column(Date, nullable=False)
    enrollment_status: Mapped[str] = mapped_column(String(50), default="ENROLLED", nullable=False)
    # Statuses: ENROLLED, COMPLETED, PROMOTED, DETAINED, REPEAT, WITHDRAWN
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="enrollments")


# ==============================================================================
# 4. Student Lifecycle Audit Events
# ==============================================================================

class StudentLifecycleEvent(AuditBaseModel):
    """
    Immutable audit trail capturing all student status transitions, promotions,
    and administrative lifecycle changes.
    """
    __tablename__ = "student_lifecycle_events"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: ADMISSION, STATUS_CHANGE, ENROLLMENT, SEMESTER_PROMOTION, SECTION_ASSIGNED, SUSPENSION, REINSTATEMENT, GRADUATION, WITHDRAWAL
    previous_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    performed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="lifecycle_events")
