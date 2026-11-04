import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.response import BaseSchema


# ==============================================================================
# 1. Student Academic Records Schemas
# ==============================================================================

class StudentAcademicRecordBase(BaseModel):
    qualification: str = Field(..., max_length=100, description="Degree or certificate (e.g. 10th, 12th/HSC, Diploma)")
    institution_name: str = Field(..., max_length=255, description="School, college or institute name")
    board_or_university: str = Field(..., max_length=255, description="Examining board or awarding university")
    year_of_passing: int = Field(..., ge=1950, le=2100, description="Year of qualification completion")
    percentage_or_cgpa: str = Field(..., max_length=50, description="Marks percentage or CGPA")
    register_number: Optional[str] = Field(None, max_length=100, description="Previous roll or register number")
    stream_or_specialization: Optional[str] = Field(None, max_length=100, description="Stream (e.g. Science, MPC, CS)")
    remarks: Optional[str] = Field(None, description="Additional verification remarks")


class StudentAcademicRecordCreate(StudentAcademicRecordBase):
    pass


class StudentAcademicRecordResponse(StudentAcademicRecordBase, BaseSchema):
    id: uuid.UUID
    student_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# 2. Student Enrollment Schemas
# ==============================================================================

class StudentEnrollmentBase(BaseModel):
    academic_year_id: uuid.UUID = Field(..., description="Academic year identifier")
    semester_id: Optional[uuid.UUID] = Field(None, description="Operational semester identifier")
    program_id: uuid.UUID = Field(..., description="Academic program identifier")
    batch_id: Optional[uuid.UUID] = Field(None, description="Cohort batch identifier")
    section_id: Optional[uuid.UUID] = Field(None, description="Classroom section identifier")
    semester_number: int = Field(..., ge=1, le=12, description="Semester level (1 to 12)")
    enrollment_date: date = Field(..., description="Enrollment registration date")
    enrollment_status: str = Field(default="ENROLLED", description="Enrollment state (ENROLLED, COMPLETED, PROMOTED, etc.)")
    remarks: Optional[str] = Field(None, description="Enrollment notes or special condition")


class StudentEnrollmentCreate(StudentEnrollmentBase):
    pass


class StudentEnrollmentResponse(StudentEnrollmentBase, BaseSchema):
    id: uuid.UUID
    student_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# 3. Student Lifecycle Event Schemas
# ==============================================================================

class StudentLifecycleEventResponse(BaseSchema):
    id: uuid.UUID
    student_id: uuid.UUID
    event_type: str
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    reason: Optional[str] = None
    performed_by_id: Optional[uuid.UUID] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime


# ==============================================================================
# 4. Student Master Schemas
# ==============================================================================

class StudentBase(BaseModel):
    admission_number: str = Field(..., max_length=50, description="Unique permanent institutional admission number")
    register_number: Optional[str] = Field(None, max_length=50, description="University examination register number")
    roll_number: Optional[str] = Field(None, max_length=50, description="Section class roll number")

    # Demographic & Personal
    first_name: str = Field(..., max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., max_length=100)
    date_of_birth: date = Field(..., description="Date of birth")
    gender: str = Field(..., max_length=20, description="MALE, FEMALE, OTHER")
    blood_group: Optional[str] = Field(None, max_length=20)
    nationality: str = Field(default="Indian", max_length=50)
    religion: Optional[str] = Field(None, max_length=50)
    community: Optional[str] = Field(None, max_length=50)
    caste: Optional[str] = Field(None, max_length=100)
    aadhar_number: Optional[str] = Field(None, max_length=20)

    # Contact & Address
    personal_email: Optional[EmailStr] = None
    institutional_email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    permanent_address: Optional[str] = None
    current_address: Optional[str] = None

    # Parents / Guardians
    father_name: Optional[str] = Field(None, max_length=100)
    father_phone: Optional[str] = Field(None, max_length=50)
    father_occupation: Optional[str] = Field(None, max_length=100)
    mother_name: Optional[str] = Field(None, max_length=100)
    mother_phone: Optional[str] = Field(None, max_length=50)
    mother_occupation: Optional[str] = Field(None, max_length=100)
    guardian_name: Optional[str] = Field(None, max_length=100)
    guardian_phone: Optional[str] = Field(None, max_length=50)

    # Academic Associations
    department_id: uuid.UUID = Field(..., description="Academic department organizational unit ID")
    program_id: uuid.UUID = Field(..., description="Degree academic program ID")
    batch_id: Optional[uuid.UUID] = Field(None, description="Admitted batch ID")
    section_id: Optional[uuid.UUID] = Field(None, description="Classroom section ID")

    # Lifecycle & Admission
    admission_date: date = Field(..., description="Official date of admission")
    admission_category: str = Field(default="REGULAR", max_length=50, description="REGULAR, MANAGEMENT, GOVT_QUOTA, LATERAL_ENTRY, etc.")
    current_semester: int = Field(default=1, ge=1, le=12)
    student_status: str = Field(default="ADMITTED", max_length=50)
    extra_data: Optional[Dict[str, Any]] = None


class StudentCreate(StudentBase):
    initial_academic_records: Optional[List[StudentAcademicRecordCreate]] = Field(
        default=None,
        description="Optional list of prior academic history records to save on admission",
    )


class StudentUpdate(BaseModel):
    register_number: Optional[str] = Field(None, max_length=50)
    roll_number: Optional[str] = Field(None, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    blood_group: Optional[str] = Field(None, max_length=20)
    nationality: Optional[str] = Field(None, max_length=50)
    religion: Optional[str] = Field(None, max_length=50)
    community: Optional[str] = Field(None, max_length=50)
    caste: Optional[str] = Field(None, max_length=100)
    aadhar_number: Optional[str] = Field(None, max_length=20)

    personal_email: Optional[EmailStr] = None
    institutional_email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    permanent_address: Optional[str] = None
    current_address: Optional[str] = None

    father_name: Optional[str] = Field(None, max_length=100)
    father_phone: Optional[str] = Field(None, max_length=50)
    father_occupation: Optional[str] = Field(None, max_length=100)
    mother_name: Optional[str] = Field(None, max_length=100)
    mother_phone: Optional[str] = Field(None, max_length=50)
    mother_occupation: Optional[str] = Field(None, max_length=100)
    guardian_name: Optional[str] = Field(None, max_length=100)
    guardian_phone: Optional[str] = Field(None, max_length=50)

    department_id: Optional[uuid.UUID] = None
    program_id: Optional[uuid.UUID] = None
    batch_id: Optional[uuid.UUID] = None
    section_id: Optional[uuid.UUID] = None
    admission_category: Optional[str] = Field(None, max_length=50)
    extra_data: Optional[Dict[str, Any]] = None


class StudentStatusUpdate(BaseModel):
    new_status: str = Field(..., max_length=50, description="New status: ADMITTED, ACTIVE, ON_LEAVE, SUSPENDED, DISCONTINUED, ALUMNI, WITHDRAWN")
    reason: Optional[str] = Field(None, description="Official administrative reason for status change")
    performed_by_id: Optional[uuid.UUID] = Field(None, description="User ID of the approving officer")


class StudentSectionAssign(BaseModel):
    batch_id: Optional[uuid.UUID] = Field(None, description="Batch to assign")
    section_id: Optional[uuid.UUID] = Field(None, description="Section to assign")
    roll_number: Optional[str] = Field(None, max_length=50, description="Class roll number")
    reason: Optional[str] = Field(None, description="Administrative re-assignment note")


class StudentResponse(StudentBase, BaseSchema):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    status_change_date: Optional[date] = None
    status_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class StudentDetailResponse(StudentResponse):
    academic_records: List[StudentAcademicRecordResponse] = Field(default_factory=list)
    enrollments: List[StudentEnrollmentResponse] = Field(default_factory=list)
    lifecycle_events: List[StudentLifecycleEventResponse] = Field(default_factory=list)
