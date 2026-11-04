import uuid
from datetime import date, datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ==============================================================================
# Base Schema Configuration
# ==============================================================================

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# University Schemas
# ==============================================================================

class UniversityCreate(BaseSchema):
    code: str = Field(..., max_length=50, examples=["JEPPIAAR"])
    name: str = Field(..., max_length=255, examples=["Jeppiaar University"])
    legal_name: Optional[str] = Field(None, max_length=255)
    establishment_year: Optional[int] = Field(None, ge=1800, le=2100)
    website: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    status: str = Field(default="active", max_length=50)


class UniversityUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    establishment_year: Optional[int] = Field(None, ge=1800, le=2100)
    website: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)


class UniversityResponse(BaseSchema):
    id: uuid.UUID
    code: str
    name: str
    legal_name: Optional[str] = None
    establishment_year: Optional[int] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# Organizational Unit Schemas
# ==============================================================================

class OrganizationalUnitCreate(BaseSchema):
    university_id: uuid.UUID
    parent_unit_id: Optional[uuid.UUID] = None
    code: str = Field(..., max_length=50, examples=["SOE", "CSE", "COE"])
    name: str = Field(..., max_length=255, examples=["School of Engineering and Technology"])
    unit_type: str = Field(
        ...,
        max_length=50,
        description="Classification: SCHOOL, DEPARTMENT, FUNCTIONAL_UNIT, ADMINISTRATIVE_UNIT, RESEARCH_CENTRE, SUPPORT_UNIT, CAMPUS",
    )
    description: Optional[str] = None
    status: str = Field(default="active", max_length=50)
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None


class OrganizationalUnitUpdate(BaseSchema):
    parent_unit_id: Optional[uuid.UUID] = None
    name: Optional[str] = Field(None, max_length=255)
    unit_type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None


class OrganizationalUnitResponse(BaseSchema):
    id: uuid.UUID
    university_id: uuid.UUID
    parent_unit_id: Optional[uuid.UUID] = None
    code: str
    name: str
    unit_type: str
    description: Optional[str] = None
    status: str
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class OrganizationalUnitTreeResponse(BaseSchema):
    id: uuid.UUID
    code: str
    name: str
    unit_type: str
    status: str
    children: List["OrganizationalUnitTreeResponse"] = Field(default_factory=list)


# ==============================================================================
# Organizational Relationship Schemas
# ==============================================================================

class OrganizationalRelationshipCreate(BaseSchema):
    source_unit_id: uuid.UUID
    target_unit_id: uuid.UUID
    relationship_type: str = Field(
        ...,
        max_length=50,
        description="ADMINISTRATIVE_PARENT, FUNCTIONAL_COORDINATION, REPORTING_TO, ACADEMIC_COORDINATION, AFFILIATION",
    )
    description: Optional[str] = None
    status: str = Field(default="active", max_length=50)
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None


class OrganizationalRelationshipResponse(BaseSchema):
    id: uuid.UUID
    source_unit_id: uuid.UUID
    target_unit_id: uuid.UUID
    relationship_type: str
    description: Optional[str] = None
    status: str
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# Academic Year & Semester Schemas
# ==============================================================================

class AcademicYearCreate(BaseSchema):
    university_id: uuid.UUID
    year_name: str = Field(..., max_length=50, examples=["2026-2027"])
    start_date: date
    end_date: date
    is_current: bool = False
    status: str = Field(default="active", max_length=50)


class AcademicYearUpdate(BaseSchema):
    year_name: Optional[str] = Field(None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=50)


class AcademicYearResponse(BaseSchema):
    id: uuid.UUID
    university_id: uuid.UUID
    year_name: str
    start_date: date
    end_date: date
    is_current: bool
    status: str
    created_at: datetime
    updated_at: datetime


class SemesterCreate(BaseSchema):
    academic_year_id: uuid.UUID
    semester_number: int = Field(..., ge=1, le=12)
    semester_name: str = Field(..., max_length=100, examples=["Odd Semester 2026"])
    semester_type: str = Field(default="ODD", max_length=20)
    start_date: date
    end_date: date
    is_current: bool = False
    status: str = Field(default="upcoming", max_length=50)


class SemesterUpdate(BaseSchema):
    semester_number: Optional[int] = Field(None, ge=1, le=12)
    semester_name: Optional[str] = Field(None, max_length=100)
    semester_type: Optional[str] = Field(None, max_length=20)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=50)


class SemesterResponse(BaseSchema):
    id: uuid.UUID
    academic_year_id: uuid.UUID
    semester_number: int
    semester_name: str
    semester_type: str
    start_date: date
    end_date: date
    is_current: bool
    status: str
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# Academic Program & Specialization Schemas
# ==============================================================================

class AcademicProgramCreate(BaseSchema):
    department_id: uuid.UUID
    program_code: str = Field(..., max_length=50, examples=["BTECH-CSE"])
    program_name: str = Field(..., max_length=255, examples=["Bachelor of Technology in Computer Science and Engineering"])
    program_type: str = Field(
        ...,
        max_length=50,
        description="UNDERGRADUATE, POSTGRADUATE, DOCTORAL, DIPLOMA",
    )
    duration_years: int = Field(default=4, ge=1, le=7)
    total_semesters: int = Field(default=8, ge=1, le=14)
    degree_awarded: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="active", max_length=50)
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None


class AcademicProgramUpdate(BaseSchema):
    program_name: Optional[str] = Field(None, max_length=255)
    program_type: Optional[str] = Field(None, max_length=50)
    duration_years: Optional[int] = Field(None, ge=1, le=7)
    total_semesters: Optional[int] = Field(None, ge=1, le=14)
    degree_awarded: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=50)
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None


class AcademicProgramResponse(BaseSchema):
    id: uuid.UUID
    department_id: uuid.UUID
    program_code: str
    program_name: str
    program_type: str
    duration_years: int
    total_semesters: int
    degree_awarded: Optional[str] = None
    status: str
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class SpecializationCreate(BaseSchema):
    program_id: uuid.UUID
    specialization_code: str = Field(..., max_length=50, examples=["AI-ML"])
    specialization_name: str = Field(..., max_length=255, examples=["Artificial Intelligence and Machine Learning"])
    description: Optional[str] = None
    status: str = Field(default="active", max_length=50)


class SpecializationResponse(BaseSchema):
    id: uuid.UUID
    program_id: uuid.UUID
    specialization_code: str
    specialization_name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# Course Schemas
# ==============================================================================

class CourseCreate(BaseSchema):
    department_id: uuid.UUID
    course_code: str = Field(..., max_length=50, examples=["CS101"])
    course_name: str = Field(..., max_length=255, examples=["Data Structures and Algorithms"])
    course_type: str = Field(default="THEORY", max_length=50)
    credits: int = Field(default=3, ge=0, le=30)
    lecture_hours: int = Field(default=3, ge=0, le=40)
    tutorial_hours: int = Field(default=0, ge=0, le=40)
    practical_hours: int = Field(default=0, ge=0, le=40)
    description: Optional[str] = None
    status: str = Field(default="active", max_length=50)
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None


class CourseUpdate(BaseSchema):
    course_name: Optional[str] = Field(None, max_length=255)
    course_type: Optional[str] = Field(None, max_length=50)
    credits: Optional[int] = Field(None, ge=0, le=30)
    lecture_hours: Optional[int] = Field(None, ge=0, le=40)
    tutorial_hours: Optional[int] = Field(None, ge=0, le=40)
    practical_hours: Optional[int] = Field(None, ge=0, le=40)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None


class CourseResponse(BaseSchema):
    id: uuid.UUID
    department_id: uuid.UUID
    course_code: str
    course_name: str
    course_type: str
    credits: int
    lecture_hours: int
    tutorial_hours: int
    practical_hours: int
    description: Optional[str] = None
    status: str
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# Batch & Section Schemas
# ==============================================================================

class AcademicBatchCreate(BaseSchema):
    program_id: uuid.UUID
    academic_year_id: Optional[uuid.UUID] = None
    batch_name: str = Field(..., max_length=100, examples=["2023-2027"])
    admission_year: int = Field(..., ge=2000, le=2100)
    graduation_year: int = Field(..., ge=2000, le=2100)
    current_semester_number: int = Field(default=1, ge=1, le=14)
    status: str = Field(default="active", max_length=50)


class AcademicBatchUpdate(BaseSchema):
    batch_name: Optional[str] = Field(None, max_length=100)
    academic_year_id: Optional[uuid.UUID] = None
    current_semester_number: Optional[int] = Field(None, ge=1, le=14)
    status: Optional[str] = Field(None, max_length=50)


class AcademicBatchResponse(BaseSchema):
    id: uuid.UUID
    program_id: uuid.UUID
    academic_year_id: Optional[uuid.UUID] = None
    batch_name: str
    admission_year: int
    graduation_year: int
    current_semester_number: int
    status: str
    created_at: datetime
    updated_at: datetime


class SectionCreate(BaseSchema):
    batch_id: uuid.UUID
    program_id: uuid.UUID
    academic_year_id: Optional[uuid.UUID] = None
    section_name: str = Field(..., max_length=50, examples=["A", "B", "CSE-1"])
    capacity: int = Field(default=60, ge=1, le=200)
    status: str = Field(default="active", max_length=50)


class SectionUpdate(BaseSchema):
    section_name: Optional[str] = Field(None, max_length=50)
    capacity: Optional[int] = Field(None, ge=1, le=200)
    status: Optional[str] = Field(None, max_length=50)


class SectionResponse(BaseSchema):
    id: uuid.UUID
    batch_id: uuid.UUID
    program_id: uuid.UUID
    academic_year_id: Optional[uuid.UUID] = None
    section_name: str
    capacity: int
    status: str
    created_at: datetime
    updated_at: datetime
