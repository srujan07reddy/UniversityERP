import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field

from app.schemas.response import BaseSchema


# ==============================================================================
# 1. Staff Qualification Schemas
# ==============================================================================

class StaffQualificationBase(BaseModel):
    degree: str = Field(..., max_length=100, description="Degree or certificate name (e.g. Ph.D., M.Tech, B.E.)")
    discipline_or_field: str = Field(..., max_length=150, description="Academic discipline or specialization")
    institution_name: str = Field(..., max_length=255, description="College or Institute where degree was earned")
    board_or_university: str = Field(..., max_length=255, description="Awarding university or certifying board")
    year_of_passing: int = Field(..., ge=1950, le=2100, description="Graduation year")
    percentage_or_cgpa: Optional[str] = Field(None, max_length=50, description="Grade, percentage or CGPA")
    certificate_url: Optional[str] = Field(None, max_length=255, description="Document reference URL")
    remarks: Optional[str] = Field(None, description="Additional notes or honors")


class StaffQualificationCreate(StaffQualificationBase):
    pass


class StaffQualificationResponse(StaffQualificationBase, BaseSchema):
    id: uuid.UUID
    staff_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# 2. Staff Experience Schemas
# ==============================================================================

class StaffExperienceBase(BaseModel):
    organization_name: str = Field(..., max_length=255, description="Employer or institutional organization")
    designation: str = Field(..., max_length=100, description="Job title held")
    experience_type: str = Field(default="TEACHING", max_length=50, description="TEACHING, INDUSTRY, RESEARCH, ADMINISTRATIVE")
    start_date: date = Field(..., description="Employment start date")
    end_date: Optional[date] = Field(None, description="Employment end date (null if current)")
    roles_and_responsibilities: Optional[str] = Field(None, description="Key duties and deliverables")
    relieving_reason: Optional[str] = Field(None, max_length=255, description="Reason for transition")


class StaffExperienceCreate(StaffExperienceBase):
    pass


class StaffExperienceResponse(StaffExperienceBase, BaseSchema):
    id: uuid.UUID
    staff_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# 3. Staff Lifecycle Event Schemas
# ==============================================================================

class StaffLifecycleEventResponse(BaseSchema):
    id: uuid.UUID
    staff_id: uuid.UUID
    event_type: str
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    reason: Optional[str] = None
    performed_by_id: Optional[uuid.UUID] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime


# ==============================================================================
# 4. Staff Department Affiliation Schemas
# ==============================================================================

class StaffDepartmentAffiliationBase(BaseModel):
    department_id: uuid.UUID = Field(..., description="Target department or center unit ID")
    affiliation_type: str = Field(default="SECONDARY", max_length=50, description="PRIMARY, SECONDARY, JOINT, ADJUNCT, VISITING, ADMINISTRATIVE_ASSIGNMENT")
    role_title: Optional[str] = Field(None, max_length=100, description="Title in affiliated unit")
    start_date: date = Field(..., description="Affiliation commencement date")
    end_date: Optional[date] = Field(None, description="Affiliation termination date")
    is_active: bool = Field(default=True, description="Whether affiliation is currently active")
    remarks: Optional[str] = Field(None, description="Administrative remarks or appointment order")


class StaffDepartmentAffiliationCreate(StaffDepartmentAffiliationBase):
    pass


class StaffDepartmentAffiliationResponse(StaffDepartmentAffiliationBase, BaseSchema):
    id: uuid.UUID
    staff_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# 5. Staff Master Schemas
# ==============================================================================

class StaffBase(BaseModel):
    staff_id: str = Field(..., max_length=50, description="Unique permanent institutional employee code")
    biometric_id: Optional[str] = Field(None, max_length=50, description="RFID / Biometric attendance hardware ID")

    # Demographic & Personal
    first_name: str = Field(..., max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., max_length=100)
    date_of_birth: date = Field(..., description="Date of birth")
    gender: str = Field(..., max_length=20, description="MALE, FEMALE, OTHER")
    blood_group: Optional[str] = Field(None, max_length=20)
    nationality: str = Field(default="Indian", max_length=50)
    pan_number: Optional[str] = Field(None, max_length=20)
    aadhar_number: Optional[str] = Field(None, max_length=20)

    # Contact & Communication
    personal_email: Optional[EmailStr] = None
    institutional_email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    permanent_address: Optional[str] = None
    current_address: Optional[str] = None

    # Employment Details (Designation != RBAC Role)
    staff_type: str = Field(..., max_length=50, description="TEACHING, NON_TEACHING, ADMINISTRATIVE, TECHNICAL, EXECUTIVE, SUPPORT")
    employment_type: str = Field(default="REGULAR", max_length=50, description="REGULAR, PROBATION, CONTRACT, AD_HOC, VISITING, ADJUNCT")
    designation: str = Field(..., max_length=100, description="Institutional job title (e.g. Professor, Assistant Professor, Lab Technician)")
    highest_qualification: Optional[str] = Field(None, max_length=200)
    specialization_area: Optional[str] = Field(None, max_length=200)

    # Organizational Associations
    department_id: uuid.UUID = Field(..., description="Primary departmental organizational unit ID")
    school_id: Optional[uuid.UUID] = Field(None, description="Constituent School organizational unit ID")

    # Joining & Relieving
    date_of_joining: date = Field(..., description="Date of employment commencement")
    probation_end_date: Optional[date] = None
    date_of_relieving: Optional[date] = None
    relieving_reason: Optional[str] = None
    notice_period_days: int = Field(default=30, ge=0)

    # Employment Status
    employment_status: str = Field(default="ACTIVE", max_length=50)
    extra_data: Optional[Dict[str, Any]] = None


class StaffCreate(StaffBase):
    initial_qualifications: Optional[List[StaffQualificationCreate]] = Field(
        default=None,
        description="Optional list of academic qualifications to persist on appointment",
    )
    initial_experience: Optional[List[StaffExperienceCreate]] = Field(
        default=None,
        description="Optional list of prior employment experience records",
    )


class StaffUpdate(BaseModel):
    biometric_id: Optional[str] = Field(None, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    blood_group: Optional[str] = Field(None, max_length=20)
    nationality: Optional[str] = Field(None, max_length=50)
    pan_number: Optional[str] = Field(None, max_length=20)
    aadhar_number: Optional[str] = Field(None, max_length=20)

    personal_email: Optional[EmailStr] = None
    institutional_email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    permanent_address: Optional[str] = None
    current_address: Optional[str] = None

    staff_type: Optional[str] = Field(None, max_length=50)
    employment_type: Optional[str] = Field(None, max_length=50)
    highest_qualification: Optional[str] = Field(None, max_length=200)
    specialization_area: Optional[str] = Field(None, max_length=200)
    probation_end_date: Optional[date] = None
    notice_period_days: Optional[int] = Field(None, ge=0)
    extra_data: Optional[Dict[str, Any]] = None


class StaffStatusUpdate(BaseModel):
    new_status: str = Field(..., max_length=50, description="New status: ACTIVE, PROBATION, ON_LEAVE, SUSPENDED, RESIGNED, RETIRED, TERMINATED, RELIEVED")
    reason: Optional[str] = Field(None, description="Official administrative reason for status change")
    date_of_relieving: Optional[date] = Field(None, description="Official date of relieving if exiting")
    performed_by_id: Optional[uuid.UUID] = Field(None, description="Approving authority user ID")


class StaffDesignationUpdate(BaseModel):
    new_designation: str = Field(..., max_length=100, description="Updated institutional job title")
    reason: Optional[str] = Field(None, description="Promotion / Re-designation administrative order")
    effective_date: Optional[date] = None


class StaffDepartmentTransfer(BaseModel):
    new_department_id: uuid.UUID = Field(..., description="Target department organizational unit ID")
    new_school_id: Optional[uuid.UUID] = Field(None, description="Target constituent school unit ID")
    reason: Optional[str] = Field(None, description="Transfer / re-assignment administrative order")


class StaffResponse(StaffBase, BaseSchema):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    status_change_date: Optional[date] = None
    status_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class StaffDetailResponse(StaffResponse):
    qualifications: List[StaffQualificationResponse] = Field(default_factory=list)
    experience_records: List[StaffExperienceResponse] = Field(default_factory=list)
    department_affiliations: List[StaffDepartmentAffiliationResponse] = Field(default_factory=list)
    lifecycle_events: List[StaffLifecycleEventResponse] = Field(default_factory=list)
