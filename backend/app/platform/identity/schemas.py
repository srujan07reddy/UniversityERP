import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==============================================================================
# Base Schema Configuration
# ==============================================================================

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# User Profile Schemas
# ==============================================================================

class UserProfileCreate(BaseSchema):
    first_name: str = Field(..., max_length=100, examples=["John"])
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., max_length=100, examples=["Doe"])
    display_name: Optional[str] = Field(None, max_length=200)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=50, examples=["MALE", "FEMALE", "OTHER"])
    blood_group: Optional[str] = Field(None, max_length=20, examples=["O+", "B+"])
    avatar_url: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(default="India", max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)


class UserProfileUpdate(BaseSchema):
    first_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=50)
    blood_group: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)


class UserProfileResponse(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    display_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# User Account Schemas
# ==============================================================================

class UserCreate(BaseSchema):
    username: str = Field(..., min_length=3, max_length=100, examples=["student.john"])
    email: EmailStr = Field(..., examples=["john.doe@jeppiaar.ac.in"])
    password: str = Field(..., min_length=8, max_length=128, description="Plaintext password to be hashed with Argon2id")
    phone: Optional[str] = Field(None, max_length=50, examples=["+919876543210"])
    user_type: str = Field(
        default="STUDENT",
        description="Classification: STUDENT, FACULTY, STAFF, ALUMNI, EXTERNAL, SYSTEM",
    )
    profile: Optional[UserProfileCreate] = None


class UserUpdate(BaseSchema):
    phone: Optional[str] = Field(None, max_length=50)
    user_type: Optional[str] = Field(None, max_length=50)


class UserStatusUpdate(BaseSchema):
    account_status: str = Field(
        ...,
        description="PENDING_ACTIVATION, ACTIVE, SUSPENDED, DEACTIVATED, LOCKED",
    )
    reason: Optional[str] = Field(None, description="Reason for status transition for audit trail")


class UserPasswordChange(BaseSchema):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=128)


class UserPasswordResetRequest(BaseSchema):
    identifier: str = Field(..., description="Username or institutional email address")


class UserPasswordResetConfirm(BaseSchema):
    token: str = Field(..., description="Secure recovery token delivered out-of-band")
    new_password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseSchema):
    id: uuid.UUID
    username: str
    email: str
    phone: Optional[str] = None
    user_type: str
    account_status: str
    email_verified: bool
    phone_verified: bool
    mfa_enabled: bool
    last_login_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    deactivated_at: Optional[datetime] = None
    deactivation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    profile: Optional[UserProfileResponse] = None


# ==============================================================================
# Account Recovery & Lifecycle Schemas
# ==============================================================================

class UserRecoveryTokenResponse(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    token_type: str
    expires_at: datetime
    created_at: datetime


class UserLifecycleEventResponse(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    event_type: str
    performed_by_id: Optional[uuid.UUID] = None
    reason: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class UserActionReasonRequest(BaseModel):
    reason: str = Field(..., min_length=3, description="Official administrative justification")
    performed_by_id: Optional[uuid.UUID] = Field(None, description="Administrator user ID authorizing the action")


# ==============================================================================
# Identity Relationship Schemas (Stage 3.5)
# ==============================================================================

class UserOrganizationMembershipBase(BaseModel):
    unit_id: uuid.UUID = Field(..., description="Organizational unit identifier")
    membership_type: str = Field(default="MEMBER", max_length=50, description="PRIMARY, MEMBER, AFFILIATE, REPRESENTATIVE, CHAIR, COMMITTEE_MEMBER")
    is_primary: bool = Field(default=False, description="Whether this unit is the primary organizational affiliation")
    effective_from: date = Field(..., description="Affiliation start date")
    effective_until: Optional[date] = Field(None, description="Affiliation end date")
    status: str = Field(default="ACTIVE", max_length=50, description="ACTIVE, INACTIVE, EXPIRED")
    notes: Optional[str] = Field(None, description="Administrative notes regarding membership")


class UserOrganizationMembershipCreate(UserOrganizationMembershipBase):
    pass


class UserOrganizationMembershipResponse(UserOrganizationMembershipBase, BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UserLinkStudentRequest(BaseModel):
    user_id: uuid.UUID = Field(..., description="Central User identity ID")
    student_id: uuid.UUID = Field(..., description="Student master record ID")
    reason: Optional[str] = Field(None, description="Administrative reason for credential linkage")


class UserLinkStaffRequest(BaseModel):
    user_id: uuid.UUID = Field(..., description="Central User identity ID")
    staff_id: uuid.UUID = Field(..., description="Staff master record ID")
    reason: Optional[str] = Field(None, description="Administrative reason for credential linkage")


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


class IdentityFootprintResponse(BaseSchema):
    user_id: uuid.UUID
    username: str
    email: str
    user_type: str
    account_status: str
    linked_student: Optional[Dict[str, Any]] = None
    linked_staff: Optional[Dict[str, Any]] = None
    organization_memberships: List[UserOrganizationMembershipResponse] = Field(default_factory=list)


# ==============================================================================
# Authentication Schemas (Stage 3.7)
# ==============================================================================

class LoginRequest(BaseSchema):
    username_or_email: str = Field(..., min_length=3, max_length=255, examples=["student.john", "john.doe@jeppiaar.ac.in"])
    password: str = Field(..., min_length=1, max_length=128)
    device_info: Optional[str] = Field(None, max_length=255, examples=["Chrome 122 on Windows 11", "Jeppiaar Android App v1.0"])


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expiration window in seconds")
    user: UserResponse


class RefreshTokenRequest(BaseSchema):
    refresh_token: str = Field(..., min_length=10)
    device_info: Optional[str] = Field(None, max_length=255)


class LogoutRequest(BaseSchema):
    refresh_token: Optional[str] = Field(None, description="Optional refresh token to revoke alongside access token")


class TokenRevokeRequest(BaseSchema):
    token: str = Field(..., description="Access or refresh token to immediately revoke")
    reason: Optional[str] = Field(None, max_length=255, description="Administrative or user revocation justification")

