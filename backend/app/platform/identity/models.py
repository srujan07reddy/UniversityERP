import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditBaseModel


# ==============================================================================
# 1. Central User Entity
# ==============================================================================

class User(AuditBaseModel):
    """
    Central user identity across all institutional roles (students, faculty, staff).
    Stores core authentication credentials, account state, and lifecycle markers.
    """
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    user_type: Mapped[str] = mapped_column(String(50), default="STUDENT", nullable=False, index=True)
    # Types: STUDENT, FACULTY, STAFF, ALUMNI, EXTERNAL, SYSTEM
    account_status: Mapped[str] = mapped_column(String(50), default="PENDING_ACTIVATION", nullable=False, index=True)
    # Statuses: PENDING_ACTIVATION, ACTIVE, SUSPENDED, DEACTIVATED, LOCKED

    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Security & Brute-force lockout protection
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Activity and lifecycle timestamps
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_password_change_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deactivation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    recovery_tokens: Mapped[List["UserRecoveryToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    lifecycle_events: Mapped[List["UserLifecycleEvent"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    student: Mapped[Optional["Student"]] = relationship(  # type: ignore[name-defined]
        "Student",
        back_populates="user",
        uselist=False,
    )
    staff: Mapped[Optional["Staff"]] = relationship(  # type: ignore[name-defined]
        "Staff",
        back_populates="user",
        uselist=False,
    )
    organization_memberships: Mapped[List["UserOrganizationMembership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    refresh_tokens: Mapped[List["UserRefreshToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    revoked_tokens: Mapped[List["RevokedToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


# ==============================================================================
# 2. User Profile Entity
# ==============================================================================

class UserProfile(AuditBaseModel):
    """
    Personal and demographic information linked to a central User.
    Contains contact, location, and emergency data.
    """
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    blood_group: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Address / Contact
    address_line1: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), default="India", nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Emergency Contact
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emergency_contact_relationship: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="profile")


# ==============================================================================
# 3. Account Recovery Tokens
# ==============================================================================

class UserRecoveryToken(AuditBaseModel):
    """
    Cryptographic tokens for activation, password reset, and account recovery.
    Stores only SHA-256 hashed token digests for security defense-in-depth.
    """
    __tablename__ = "user_recovery_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    token_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: ACTIVATION, PASSWORD_RESET, MFA_RECOVERY, EMAIL_VERIFICATION
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="recovery_tokens")


# ==============================================================================
# 4. Identity Lifecycle Audit Events
# ==============================================================================

class UserLifecycleEvent(AuditBaseModel):
    """
    Immutable audit log recording identity events (creation, status changes, lockouts).
    Guarantees full administrative and compliance traceability.
    """
    __tablename__ = "user_lifecycle_events"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: CREATED, ACTIVATED, SUSPENDED, REINSTATED, DEACTIVATED, PASSWORD_CHANGED, PASSWORD_RESET_REQUESTED, LOCKED_OUT, UNLOCKED
    performed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="lifecycle_events")


# ==============================================================================
# 5. User Organization Memberships (Multi-organizational Affiliations)
# ==============================================================================

class UserOrganizationMembership(AuditBaseModel):
    """
    Explicit organizational unit memberships for a user.
    Supports multiple concurrent organizational affiliations across schools,
    departments, centres of excellence, and administrative wings.
    """
    __tablename__ = "user_organization_memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "unit_id", "membership_type", name="uq_user_unit_membership_type"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizational_units.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    membership_type: Mapped[str] = mapped_column(String(50), default="MEMBER", nullable=False, index=True)
    # Types: PRIMARY, MEMBER, AFFILIATE, REPRESENTATIVE, CHAIR, COMMITTEE_MEMBER
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False, index=True)
    # Statuses: ACTIVE, INACTIVE, EXPIRED
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="organization_memberships")
    unit: Mapped["OrganizationalUnit"] = relationship(foreign_keys=[unit_id])  # type: ignore[name-defined]


# ==============================================================================
# 6. User Refresh Tokens (Session & Token Rotation)
# ==============================================================================

class UserRefreshToken(AuditBaseModel):
    """
    Persisted refresh tokens for session management and refresh token rotation.
    Stores SHA-256 token hash, client metadata, and revocation state.
    """
    __tablename__ = "user_refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    jti: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


# ==============================================================================
# 7. Revoked Tokens (JWT Blacklist)
# ==============================================================================

class RevokedToken(AuditBaseModel):
    """
    Blacklisted access tokens and immediate revocation markers.
    Stored by JTI to allow immediate invalidation before token expiration.
    """
    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    token_type: Mapped[str] = mapped_column(String(20), default="ACCESS", nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="revoked_tokens")

