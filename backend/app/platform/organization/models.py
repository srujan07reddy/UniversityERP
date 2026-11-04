import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditBaseModel


# ==============================================================================
# 1. University Entity (Apex Institutional Authority)
# ==============================================================================

class University(AuditBaseModel):
    """
    Apex institutional authority entity representing the university charter.
    """
    __tablename__ = "universities"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    establishment_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    # Relationships
    units: Mapped[List["OrganizationalUnit"]] = relationship(
        back_populates="university",
        cascade="all, delete-orphan",
    )
    academic_years: Mapped[List["AcademicYear"]] = relationship(
        back_populates="university",
        cascade="all, delete-orphan",
    )


# ==============================================================================
# 2. Organizational Unit (Schools, Departments, Functional & Administrative Units)
# ==============================================================================

class OrganizationalUnit(AuditBaseModel):
    """
    Constituent organizational units: Academic Schools, Departments,
    Functional Units (COE, Finance, IQAC, Placement), and Administrative Units.
    Supports recursive self-referential hierarchy as well as explicit relationships.
    """
    __tablename__ = "organizational_units"

    university_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("universities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizational_units.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Unit types: SCHOOL, DEPARTMENT, FUNCTIONAL_UNIT, ADMINISTRATIVE_UNIT, RESEARCH_CENTRE, SUPPORT_UNIT, CAMPUS
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Hierarchical tree relationships
    university: Mapped["University"] = relationship(back_populates="units")
    parent_unit: Mapped[Optional["OrganizationalUnit"]] = relationship(
        remote_side="OrganizationalUnit.id",
        back_populates="child_units",
    )
    child_units: Mapped[List["OrganizationalUnit"]] = relationship(
        back_populates="parent_unit",
    )

    # Domain associations
    programs: Mapped[List["AcademicProgram"]] = relationship(
        back_populates="department",
        cascade="all, delete-orphan",
    )
    courses: Mapped[List["Course"]] = relationship(
        back_populates="department",
    )

    # Explicit cross-unit relationships (non-hierarchical)
    source_relationships: Mapped[List["OrganizationalRelationship"]] = relationship(
        foreign_keys="[OrganizationalRelationship.source_unit_id]",
        back_populates="source_unit",
        cascade="all, delete-orphan",
    )
    target_relationships: Mapped[List["OrganizationalRelationship"]] = relationship(
        foreign_keys="[OrganizationalRelationship.target_unit_id]",
        back_populates="target_unit",
        cascade="all, delete-orphan",
    )


# ==============================================================================
# 3. Explicit Organizational Relationships (Non-Hierarchical & Cross-Unit)
# ==============================================================================

class OrganizationalRelationship(AuditBaseModel):
    """
    Explicitly models non-hierarchical, matrix, and coordination relationships
    between institutional units (e.g. COE to School, IQAC to Department, etc.).
    """
    __tablename__ = "organizational_relationships"

    source_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizational_units.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizational_units.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: ADMINISTRATIVE_PARENT, FUNCTIONAL_COORDINATION, REPORTING_TO, ACADEMIC_COORDINATION, AFFILIATION
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    source_unit: Mapped["OrganizationalUnit"] = relationship(
        foreign_keys=[source_unit_id],
        back_populates="source_relationships",
    )
    target_unit: Mapped["OrganizationalUnit"] = relationship(
        foreign_keys=[target_unit_id],
        back_populates="target_relationships",
    )


# ==============================================================================
# 4. Academic Years and Semesters
# ==============================================================================

class AcademicYear(AuditBaseModel):
    """
    Institutional academic year container (e.g. 2026-2027).
    """
    __tablename__ = "academic_years"

    university_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("universities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    year_name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    # Relationships
    university: Mapped["University"] = relationship(back_populates="academic_years")
    semesters: Mapped[List["Semester"]] = relationship(
        back_populates="academic_year",
        cascade="all, delete-orphan",
    )


class Semester(AuditBaseModel):
    """
    Discrete academic operational session within an Academic Year.
    """
    __tablename__ = "semesters"

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    semester_number: Mapped[int] = mapped_column(Integer, nullable=False)
    semester_name: Mapped[str] = mapped_column(String(100), nullable=False)
    semester_type: Mapped[str] = mapped_column(String(20), default="ODD", nullable=False)  # ODD, EVEN, SUMMER
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="upcoming", nullable=False)

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship(back_populates="semesters")


# ==============================================================================
# 5. Academic Programs & Specializations
# ==============================================================================

class AcademicProgram(AuditBaseModel):
    """
    Degree-granting curricula offered by a Department.
    """
    __tablename__ = "academic_programs"

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizational_units.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    program_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    program_name: Mapped[str] = mapped_column(String(255), nullable=False)
    program_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: UNDERGRADUATE, POSTGRADUATE, DOCTORAL, DIPLOMA
    duration_years: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    total_semesters: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    degree_awarded: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    department: Mapped["OrganizationalUnit"] = relationship(back_populates="programs")
    specializations: Mapped[List["Specialization"]] = relationship(
        back_populates="program",
        cascade="all, delete-orphan",
    )
    batches: Mapped[List["AcademicBatch"]] = relationship(
        back_populates="program",
        cascade="all, delete-orphan",
    )


class Specialization(AuditBaseModel):
    """
    Disciplinary concentrations and minors within an Academic Program.
    """
    __tablename__ = "specializations"

    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    specialization_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    specialization_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    # Relationships
    program: Mapped["AcademicProgram"] = relationship(back_populates="specializations")


# ==============================================================================
# 6. Courses (Institutional Course Master Catalog)
# ==============================================================================

class Course(AuditBaseModel):
    """
    Institutional course catalog item offered by an academic department.
    """
    __tablename__ = "courses"

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizational_units.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    course_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    course_name: Mapped[str] = mapped_column(String(255), nullable=False)
    course_type: Mapped[str] = mapped_column(String(50), default="THEORY", nullable=False)
    # Types: THEORY, PRACTICAL, INTEGRATED, PROJECT, SEMINAR
    credits: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    lecture_hours: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    tutorial_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    practical_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    department: Mapped["OrganizationalUnit"] = relationship(back_populates="courses")


# ==============================================================================
# 7. Batches and Sections
# ==============================================================================

class AcademicBatch(AuditBaseModel):
    """
    Cohort of students admitted to a program in a specific academic year.
    """
    __tablename__ = "academic_batches"

    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    academic_year_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    batch_name: Mapped[str] = mapped_column(String(100), nullable=False)
    admission_year: Mapped[int] = mapped_column(Integer, nullable=False)
    graduation_year: Mapped[int] = mapped_column(Integer, nullable=False)
    current_semester_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    # Statuses: admitted, active, graduated, inactive

    # Relationships
    program: Mapped["AcademicProgram"] = relationship(back_populates="batches")
    sections: Mapped[List["Section"]] = relationship(
        back_populates="batch",
        cascade="all, delete-orphan",
    )


class Section(AuditBaseModel):
    """
    Operational classroom and cohort subsection within an academic batch.
    """
    __tablename__ = "sections"

    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    academic_year_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    section_name: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    # Relationships
    batch: Mapped["AcademicBatch"] = relationship(back_populates="sections")
