import uuid
from datetime import date
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditBaseModel


# ==============================================================================
# 1. Staff Master Entity
# ==============================================================================

class Staff(AuditBaseModel):
    """
    Staff Institutional Employment Master.
    Maintains official university staff identity, employment records, designation,
    and organizational associations.
    
    IMPORTANT ARCHITECTURAL RULE:
    A staff member's designation (e.g. Professor, HOD, Technician) is strictly
    an institutional job title, NOT an application authorization role.
    Application roles and RBAC belong exclusively to the authorization layer (Phase 4).
    """
    __tablename__ = "staff"

    # Optional linkage to central User account (credential authentication handled separately)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
    )

    # Core Institutional Identifiers
    staff_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    biometric_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)

    # Personal and Demographic Details
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)  # MALE, FEMALE, OTHER
    blood_group: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    nationality: Mapped[str] = mapped_column(String(50), default="Indian", nullable=False)
    pan_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
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

    # Employment & Organizational Details
    staff_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: TEACHING, NON_TEACHING, ADMINISTRATIVE, TECHNICAL, EXECUTIVE, SUPPORT
    employment_type: Mapped[str] = mapped_column(String(50), default="REGULAR", nullable=False)
    # Types: REGULAR, PROBATION, CONTRACT, AD_HOC, VISITING, ADJUNCT
    designation: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Institutional rank/title: Professor, Assistant Professor, Associate Professor, Registrar, etc.
    highest_qualification: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    specialization_area: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Primary Department & School Associations
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizational_units.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    school_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizational_units.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    # Joining & Relieving Lifecycle Information
    date_of_joining: Mapped[date] = mapped_column(Date, nullable=False)
    probation_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    date_of_relieving: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    relieving_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notice_period_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    # Employment Status
    employment_status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False, index=True)
    # Statuses: ACTIVE, PROBATION, ON_LEAVE, SUSPENDED, RESIGNED, RETIRED, TERMINATED, RELIEVED
    status_change_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Flexible metadata
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship(  # type: ignore[name-defined]
        "User",
        foreign_keys=[user_id],
        back_populates="staff",
    )
    department: Mapped["OrganizationalUnit"] = relationship(foreign_keys=[department_id])  # type: ignore[name-defined]
    school: Mapped[Optional["OrganizationalUnit"]] = relationship(foreign_keys=[school_id])  # type: ignore[name-defined]

    qualifications: Mapped[List["StaffQualification"]] = relationship(
        back_populates="staff",
        cascade="all, delete-orphan",
        order_by="StaffQualification.year_of_passing.desc()",
    )
    experience_records: Mapped[List["StaffExperience"]] = relationship(
        back_populates="staff",
        cascade="all, delete-orphan",
        order_by="StaffExperience.start_date.desc()",
    )
    department_affiliations: Mapped[List["StaffDepartmentAffiliation"]] = relationship(
        back_populates="staff",
        cascade="all, delete-orphan",
        order_by="StaffDepartmentAffiliation.start_date.desc()",
    )
    lifecycle_events: Mapped[List["StaffLifecycleEvent"]] = relationship(
        back_populates="staff",
        cascade="all, delete-orphan",
        order_by="StaffLifecycleEvent.created_at.desc()",
    )


# ==============================================================================
# 2. Staff Qualifications
# ==============================================================================

class StaffQualification(AuditBaseModel):
    """
    Academic and professional degrees earned by a staff member
    (e.g., Ph.D., M.Tech, M.Phil, B.E., NET, SLET certifications).
    """
    __tablename__ = "staff_qualifications"

    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    degree: Mapped[str] = mapped_column(String(100), nullable=False)
    discipline_or_field: Mapped[str] = mapped_column(String(150), nullable=False)
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    board_or_university: Mapped[str] = mapped_column(String(255), nullable=False)
    year_of_passing: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage_or_cgpa: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    certificate_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    staff: Mapped["Staff"] = relationship(back_populates="qualifications")


# ==============================================================================
# 3. Staff Previous Experience
# ==============================================================================

class StaffExperience(AuditBaseModel):
    """
    Previous professional, teaching, industrial, or research employment history.
    """
    __tablename__ = "staff_experience"

    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_name: Mapped[str] = mapped_column(String(255), nullable=False)
    designation: Mapped[str] = mapped_column(String(100), nullable=False)
    experience_type: Mapped[str] = mapped_column(String(50), default="TEACHING", nullable=False)
    # Types: TEACHING, INDUSTRY, RESEARCH, ADMINISTRATIVE
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    roles_and_responsibilities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    relieving_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    staff: Mapped["Staff"] = relationship(back_populates="experience_records")


# ==============================================================================
# 4. Staff Lifecycle Audit Events
# ==============================================================================

class StaffLifecycleEvent(AuditBaseModel):
    """
    Immutable audit trail capturing all employment state transitions,
    designation revisions, department transfers, and administrative actions.
    """
    __tablename__ = "staff_lifecycle_events"

    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: APPOINTMENT, STATUS_CHANGE, DESIGNATION_CHANGE, DEPARTMENT_TRANSFER, PROBATION_CONFIRMATION, SUSPENSION, RELIEVED, RETIRED, TERMINATED
    previous_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    performed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    staff: Mapped["Staff"] = relationship(back_populates="lifecycle_events")


# ==============================================================================
# 5. Staff Department Affiliations (Secondary & Joint Department Appointments)
# ==============================================================================

class StaffDepartmentAffiliation(AuditBaseModel):
    """
    Secondary, joint, or adjunct departmental appointments for a staff member.
    Enables faculty to hold cross-departmental and research centre affiliations
    alongside their primary department appointment.
    """
    __tablename__ = "staff_department_affiliations"
    __table_args__ = (
        UniqueConstraint("staff_id", "department_id", "affiliation_type", name="uq_staff_dept_affiliation"),
    )

    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizational_units.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    affiliation_type: Mapped[str] = mapped_column(String(50), default="SECONDARY", nullable=False, index=True)
    # Types: PRIMARY, SECONDARY, JOINT, ADJUNCT, VISITING, ADMINISTRATIVE_ASSIGNMENT
    role_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    staff: Mapped["Staff"] = relationship(back_populates="department_affiliations")
    department: Mapped["OrganizationalUnit"] = relationship(foreign_keys=[department_id])  # type: ignore[name-defined]

