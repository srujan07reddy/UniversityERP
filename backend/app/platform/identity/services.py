import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationException,
    BadRequestException,
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_jwt,
    generate_secure_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.platform.identity.models import (
    RevokedToken,
    User,
    UserLifecycleEvent,
    UserOrganizationMembership,
    UserProfile,
    UserRecoveryToken,
    UserRefreshToken,
)
from app.platform.identity.repositories import (
    RevokedTokenRepository,
    UserLifecycleEventRepository,
    UserOrganizationMembershipRepository,
    UserProfileRepository,
    UserRecoveryTokenRepository,
    UserRefreshTokenRepository,
    UserRepository,
)
from app.platform.identity.schemas import (
    IdentityFootprintResponse,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserLinkStaffRequest,
    UserLinkStudentRequest,
    UserOrganizationMembershipCreate,
    UserOrganizationMembershipResponse,
    UserProfileCreate,
    UserProfileUpdate,
    UserResponse,
    UserUpdate,
)
from app.platform.organization.models import OrganizationalUnit
from app.domains.students.models import Student, StudentLifecycleEvent
from app.domains.staff.models import Staff, StaffLifecycleEvent


class UserIdentityService:
    """
    Central business service orchestrating institutional user identity,
    profile management, credential storage, and account lifecycles.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.profile_repo = UserProfileRepository(session)
        self.token_repo = UserRecoveryTokenRepository(session)
        self.event_repo = UserLifecycleEventRepository(session)
        self.membership_repo = UserOrganizationMembershipRepository(session)
        self.refresh_token_repo = UserRefreshTokenRepository(session)
        self.revoked_token_repo = RevokedTokenRepository(session)

    # --------------------------------------------------------------------------
    # Account Registration & Creation
    # --------------------------------------------------------------------------

    async def create_user(
        self,
        data: UserCreate,
        performed_by_id: Optional[uuid.UUID] = None,
        auto_activate: bool = False,
    ) -> Tuple[User, Optional[str]]:
        """
        Registers a new institutional user.
        Hashes password with Argon2id and dispatches an activation token if required.
        """
        # 1. Uniqueness verifications
        if await self.user_repo.get_by_username(data.username):
            raise ConflictException(f"Username '{data.username}' is already registered.")
        if await self.user_repo.get_by_email(data.email):
            raise ConflictException(f"Institutional email '{data.email}' is already registered.")

        # 2. Hash password with Argon2id
        hashed_password = get_password_hash(data.password)

        now = datetime.now(timezone.utc)
        initial_status = "ACTIVE" if auto_activate else "PENDING_ACTIVATION"

        user = User(
            username=data.username.strip(),
            email=data.email.strip().lower(),
            phone=data.phone.strip() if data.phone else None,
            password_hash=hashed_password,
            user_type=data.user_type,
            account_status=initial_status,
            email_verified=auto_activate,
            activated_at=now if auto_activate else None,
        )
        self.session.add(user)
        await self.session.flush()

        # 3. Create Profile if provided
        if data.profile:
            profile = UserProfile(
                user_id=user.id,
                **data.profile.model_dump(exclude_unset=True),
            )
            self.session.add(profile)
            await self.session.flush()

        # 4. Generate Activation Token if pending
        raw_token: Optional[str] = None
        if not auto_activate:
            raw_token = generate_secure_token(32)
            token_record = UserRecoveryToken(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                token_type="ACTIVATION",
                expires_at=now + timedelta(days=3),
            )
            self.session.add(token_record)

        # 5. Log lifecycle creation event
        event = UserLifecycleEvent(
            user_id=user.id,
            event_type="CREATED",
            performed_by_id=performed_by_id,
            reason="Institutional identity registered.",
            metadata_json={"user_type": user.user_type, "auto_activate": auto_activate},
        )
        self.session.add(event)
        await self.session.flush()

        # Re-fetch with profile eagerly loaded
        complete_user = await self.user_repo.get_with_profile(user.id)
        return complete_user or user, raw_token

    # --------------------------------------------------------------------------
    # Account Activation & Verification
    # --------------------------------------------------------------------------

    async def activate_account(self, raw_token: str) -> User:
        """
        Activates an account via one-time secure activation token.
        """
        digest = hash_token(raw_token.strip())
        token_record = await self.token_repo.get_active_token(digest, "ACTIVATION")
        if not token_record:
            raise BadRequestException("Invalid or expired activation token.")

        now = datetime.now(timezone.utc)
        token_record.used_at = now

        user = await self.user_repo.get_with_profile(token_record.user_id)
        if not user:
            raise NotFoundException("User account associated with this token was not found.")

        user.account_status = "ACTIVE"
        user.email_verified = True
        user.activated_at = now

        event = UserLifecycleEvent(
            user_id=user.id,
            event_type="ACTIVATED",
            performed_by_id=user.id,
            reason="Account activated via email token verification.",
        )
        self.session.add(event)
        await self.session.flush()
        return user

    # --------------------------------------------------------------------------
    # Account Lifecycle: Suspension, Deactivation & Reinstatement
    # --------------------------------------------------------------------------

    async def update_account_status(
        self,
        user_id: uuid.UUID,
        new_status: str,
        reason: Optional[str] = None,
        performed_by_id: Optional[uuid.UUID] = None,
    ) -> User:
        """
        Transitions user account status: ACTIVE, SUSPENDED, DEACTIVATED, LOCKED.
        """
        user = await self.user_repo.get_with_profile(user_id)
        if not user:
            raise NotFoundException(f"User with ID '{user_id}' not found.")

        valid_statuses = {"ACTIVE", "SUSPENDED", "DEACTIVATED", "LOCKED"}
        if new_status not in valid_statuses:
            raise ValidationException(f"Invalid account status '{new_status}'. Allowed: {valid_statuses}")

        old_status = user.account_status
        user.account_status = new_status
        now = datetime.now(timezone.utc)

        if new_status == "DEACTIVATED":
            user.deactivated_at = now
            user.deactivation_reason = reason
            event_type = "DEACTIVATED"
        elif new_status == "SUSPENDED":
            event_type = "SUSPENDED"
        elif new_status == "ACTIVE":
            user.deactivated_at = None
            user.deactivation_reason = None
            user.locked_until = None
            user.failed_login_attempts = 0
            event_type = "REINSTATED" if old_status in ("SUSPENDED", "DEACTIVATED") else "ACTIVATED"
        elif new_status == "LOCKED":
            event_type = "LOCKED_OUT"
        else:
            event_type = "STATUS_CHANGED"

        event = UserLifecycleEvent(
            user_id=user.id,
            event_type=event_type,
            performed_by_id=performed_by_id,
            reason=reason or f"Status transitioned from {old_status} to {new_status}.",
            metadata_json={"previous_status": old_status, "new_status": new_status},
        )
        self.session.add(event)
        await self.session.flush()
        return user

    async def suspend_user(
        self, user_id: uuid.UUID, reason: str, performed_by_id: Optional[uuid.UUID] = None
    ) -> User:
        user = await self.get_user(user_id)
        if user.account_status == "SUSPENDED":
            raise ConflictException("User account is already suspended.")
        return await self.update_account_status(
            user_id=user_id,
            new_status="SUSPENDED",
            reason=reason,
            performed_by_id=performed_by_id,
        )

    async def reinstate_user(
        self, user_id: uuid.UUID, reason: str, performed_by_id: Optional[uuid.UUID] = None
    ) -> User:
        user = await self.get_user(user_id)
        if user.account_status not in ("SUSPENDED", "DEACTIVATED", "LOCKED"):
            raise BadRequestException(
                f"Cannot reinstate user with status '{user.account_status}'. "
                "Only suspended, deactivated, or locked accounts can be reinstated."
            )
        return await self.update_account_status(
            user_id=user_id,
            new_status="ACTIVE",
            reason=reason,
            performed_by_id=performed_by_id,
        )

    async def deactivate_user(
        self, user_id: uuid.UUID, reason: str, performed_by_id: Optional[uuid.UUID] = None
    ) -> User:
        user = await self.get_user(user_id)
        if user.account_status == "DEACTIVATED":
            raise ConflictException("User account is already deactivated.")

        # Explicit architectural safety:
        # Deactivating an account transitions credentials & access state without deleting or cascading
        # into underlying student academic history or staff employment records.
        return await self.update_account_status(
            user_id=user_id,
            new_status="DEACTIVATED",
            reason=reason,
            performed_by_id=performed_by_id,
        )

    async def unlock_user(
        self, user_id: uuid.UUID, performed_by_id: Optional[uuid.UUID] = None
    ) -> User:
        user = await self.get_user(user_id)
        user.failed_login_attempts = 0
        user.locked_until = None
        if user.account_status == "LOCKED":
            user.account_status = "ACTIVE"

        event = UserLifecycleEvent(
            user_id=user.id,
            event_type="UNLOCKED",
            performed_by_id=performed_by_id,
            reason="Administrative account lockout reset.",
        )
        self.session.add(event)
        await self.session.flush()
        return user

    async def list_lifecycle_events(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        user_id: Optional[uuid.UUID] = None,
        event_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Tuple[Sequence[UserLifecycleEvent], int]:
        return await self.event_repo.list_events(
            offset=offset,
            limit=limit,
            user_id=user_id,
            event_type=event_type,
            from_date=from_date,
            to_date=to_date,
        )

    # --------------------------------------------------------------------------
    # User Profile Operations
    # --------------------------------------------------------------------------

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_with_profile(user_id)
        if not user:
            raise NotFoundException(f"User with ID '{user_id}' not found.")
        return user

    async def get_user_by_identifier(self, identifier: str) -> User:
        user = await self.user_repo.get_by_identifier(identifier)
        if not user:
            raise NotFoundException(f"User '{identifier}' not found.")
        return user

    async def update_profile(
        self,
        user_id: uuid.UUID,
        data: UserProfileUpdate,
        performed_by_id: Optional[uuid.UUID] = None,
    ) -> UserProfile:
        """
        Updates personal profile details. Creates profile entity if missing.
        """
        user = await self.get_user(user_id)
        profile = await self.profile_repo.get_by_user_id(user_id)

        update_fields = data.model_dump(exclude_unset=True)
        tracked_fields = list(update_fields.keys())

        if not profile:
            # Create fresh profile
            fn = update_fields.get("first_name", user.username)
            ln = update_fields.get("last_name", "User")
            other_fields = {k: v for k, v in update_fields.items() if k not in ("first_name", "last_name")}
            profile = UserProfile(
                user_id=user_id,
                first_name=fn,
                last_name=ln,
                **other_fields,
            )
            self.session.add(profile)
        else:
            for k, v in update_fields.items():
                setattr(profile, k, v)

        event = UserLifecycleEvent(
            user_id=user_id,
            event_type="PROFILE_UPDATED",
            performed_by_id=performed_by_id,
            reason="User personal profile information updated.",
            metadata_json={"updated_fields": tracked_fields},
        )
        self.session.add(event)
        await self.session.flush()
        return profile

    # --------------------------------------------------------------------------
    # Password Management & Recovery
    # --------------------------------------------------------------------------

    async def change_password(
        self,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str,
    ) -> None:
        """
        Changes user password after validating current password.
        Hashes new password with Argon2id.
        """
        user = await self.get_user(user_id)
        if not verify_password(current_password, user.password_hash):
            raise BadRequestException("Current password is incorrect.")

        user.password_hash = get_password_hash(new_password)
        now = datetime.now(timezone.utc)
        user.last_password_change_at = now

        event = UserLifecycleEvent(
            user_id=user.id,
            event_type="PASSWORD_CHANGED",
            performed_by_id=user.id,
            reason="User initiated credential change.",
        )
        self.session.add(event)
        await self.session.flush()

    async def request_password_reset(self, identifier: str) -> Optional[str]:
        """
        Initiates password reset workflow. Returns raw token for out-of-band delivery.
        Silently returns None if user does not exist to prevent identity enumeration.
        """
        user = await self.user_repo.get_by_identifier(identifier)
        if not user or user.account_status in ("DEACTIVATED", "SUSPENDED"):
            return None

        raw_token = generate_secure_token(32)
        now = datetime.now(timezone.utc)
        token_record = UserRecoveryToken(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            token_type="PASSWORD_RESET",
            expires_at=now + timedelta(hours=2),
        )
        self.session.add(token_record)

        event = UserLifecycleEvent(
            user_id=user.id,
            event_type="PASSWORD_RESET_REQUESTED",
            performed_by_id=user.id,
            reason="Password reset requested.",
        )
        self.session.add(event)
        await self.session.flush()
        return raw_token

    async def confirm_password_reset(self, raw_token: str, new_password: str) -> User:
        """
        Resets user password with a validated recovery token.
        """
        digest = hash_token(raw_token.strip())
        token_record = await self.token_repo.get_active_token(digest, "PASSWORD_RESET")
        if not token_record:
            raise BadRequestException("Invalid or expired password reset token.")

        now = datetime.now(timezone.utc)
        token_record.used_at = now

        user = await self.get_user(token_record.user_id)
        user.password_hash = get_password_hash(new_password)
        user.last_password_change_at = now
        user.locked_until = None
        user.failed_login_attempts = 0

        event = UserLifecycleEvent(
            user_id=user.id,
            event_type="PASSWORD_CHANGED",
            performed_by_id=user.id,
            reason="Password reset completed via secure recovery token.",
        )
        self.session.add(event)
        await self.session.flush()
        return user

    # --------------------------------------------------------------------------
    # Audit History
    # --------------------------------------------------------------------------

    async def get_lifecycle_history(self, user_id: uuid.UUID) -> Sequence[UserLifecycleEvent]:
        await self.get_user(user_id)
        return await self.event_repo.get_for_user(user_id)

    # --------------------------------------------------------------------------
    # Identity Relationships (Stage 3.5)
    # --------------------------------------------------------------------------

    async def link_student(self, req: UserLinkStudentRequest) -> Student:
        user = await self.get_user(req.user_id)
        student = await self.session.get(Student, req.student_id)
        if not student:
            raise NotFoundException(f"Student record with ID {req.student_id} not found.")

        query_user = await self.session.execute(select(Student).where(Student.user_id == req.user_id))
        existing_user_student = query_user.scalars().first()
        if existing_user_student and existing_user_student.id != req.student_id:
            raise ConflictException(f"User '{user.username}' is already linked to student '{existing_user_student.admission_number}'.")

        if student.user_id and student.user_id != req.user_id:
            raise ConflictException(f"Student '{student.admission_number}' is already linked to another user account.")

        student.user_id = req.user_id

        user_event = UserLifecycleEvent(
            user_id=user.id,
            event_type="LINK_STUDENT",
            reason=req.reason or f"Linked to student profile {student.admission_number}",
            metadata_json={"student_id": str(student.id), "admission_number": student.admission_number},
        )
        self.session.add(user_event)

        student_event = StudentLifecycleEvent(
            student_id=student.id,
            event_type="LINK_USER",
            reason=req.reason or f"Linked to user account {user.username}",
            metadata_json={"user_id": str(user.id), "username": user.username},
        )
        self.session.add(student_event)

        await self.session.flush()
        await self.session.refresh(student)
        return student

    async def unlink_student(self, student_id: uuid.UUID, reason: Optional[str] = None) -> Student:
        student = await self.session.get(Student, student_id)
        if not student:
            raise NotFoundException(f"Student record with ID {student_id} not found.")
        if not student.user_id:
            raise BadRequestException("Student record is not linked to any user account.")

        prev_user_id = student.user_id
        student.user_id = None

        user_event = UserLifecycleEvent(
            user_id=prev_user_id,
            event_type="UNLINK_STUDENT",
            reason=reason or f"Unlinked from student profile {student.admission_number}",
            metadata_json={"student_id": str(student.id)},
        )
        self.session.add(user_event)

        student_event = StudentLifecycleEvent(
            student_id=student.id,
            event_type="UNLINK_USER",
            reason=reason or "Unlinked from user account",
            metadata_json={"previous_user_id": str(prev_user_id)},
        )
        self.session.add(student_event)

        await self.session.flush()
        await self.session.refresh(student)
        return student

    async def link_staff(self, req: UserLinkStaffRequest) -> Staff:
        user = await self.get_user(req.user_id)
        staff = await self.session.get(Staff, req.staff_id)
        if not staff:
            raise NotFoundException(f"Staff record with ID {req.staff_id} not found.")

        query_user = await self.session.execute(select(Staff).where(Staff.user_id == req.user_id))
        existing_user_staff = query_user.scalars().first()
        if existing_user_staff and existing_user_staff.id != req.staff_id:
            raise ConflictException(f"User '{user.username}' is already linked to staff '{existing_user_staff.staff_id}'.")

        if staff.user_id and staff.user_id != req.user_id:
            raise ConflictException(f"Staff member '{staff.staff_id}' is already linked to another user account.")

        staff.user_id = req.user_id

        user_event = UserLifecycleEvent(
            user_id=user.id,
            event_type="LINK_STAFF",
            reason=req.reason or f"Linked to staff member {staff.staff_id}",
            metadata_json={"staff_id": str(staff.id), "employee_code": staff.staff_id},
        )
        self.session.add(user_event)

        staff_event = StaffLifecycleEvent(
            staff_id=staff.id,
            event_type="LINK_USER",
            reason=req.reason or f"Linked to user account {user.username}",
            metadata_json={"user_id": str(user.id), "username": user.username},
        )
        self.session.add(staff_event)

        await self.session.flush()
        await self.session.refresh(staff)
        return staff

    async def unlink_staff(self, staff_id: uuid.UUID, reason: Optional[str] = None) -> Staff:
        staff = await self.session.get(Staff, staff_id)
        if not staff:
            raise NotFoundException(f"Staff member with ID {staff_id} not found.")
        if not staff.user_id:
            raise BadRequestException("Staff member is not linked to any user account.")

        prev_user_id = staff.user_id
        staff.user_id = None

        user_event = UserLifecycleEvent(
            user_id=prev_user_id,
            event_type="UNLINK_STAFF",
            reason=reason or f"Unlinked from staff member {staff.staff_id}",
            metadata_json={"staff_id": str(staff.id)},
        )
        self.session.add(user_event)

        staff_event = StaffLifecycleEvent(
            staff_id=staff.id,
            event_type="UNLINK_USER",
            reason=reason or "Unlinked from user account",
            metadata_json={"previous_user_id": str(prev_user_id)},
        )
        self.session.add(staff_event)

        await self.session.flush()
        await self.session.refresh(staff)
        return staff

    async def add_organization_membership(
        self, user_id: uuid.UUID, data: UserOrganizationMembershipCreate
    ) -> UserOrganizationMembership:
        user = await self.get_user(user_id)
        unit = await self.session.get(OrganizationalUnit, data.unit_id)
        if not unit:
            raise NotFoundException(f"Organizational unit with ID {data.unit_id} not found.")

        norm_type = data.membership_type.strip().upper()
        existing = await self.membership_repo.get_by_user_and_unit(user_id, data.unit_id, norm_type)
        if existing:
            raise ConflictException(
                f"User already holds a '{norm_type}' membership with organizational unit '{unit.name}'."
            )

        if data.is_primary:
            query = select(UserOrganizationMembership).where(
                UserOrganizationMembership.user_id == user_id,
                UserOrganizationMembership.is_primary.is_(True),
            )
            primaries = (await self.session.execute(query)).scalars().all()
            for p in primaries:
                p.is_primary = False

        membership_dict = data.model_dump()
        membership_dict["user_id"] = user_id
        membership_dict["membership_type"] = norm_type
        membership_dict["status"] = data.status.strip().upper()

        membership = await self.membership_repo.create(membership_dict)

        event = UserLifecycleEvent(
            user_id=user.id,
            event_type="MEMBERSHIP_GRANTED",
            reason=f"Granted {norm_type} membership in {unit.name}",
            metadata_json={
                "unit_id": str(unit.id),
                "unit_name": unit.name,
                "membership_type": norm_type,
                "is_primary": data.is_primary,
            },
        )
        self.session.add(event)
        await self.session.flush()
        return membership

    async def list_user_memberships(self, user_id: uuid.UUID) -> Sequence[UserOrganizationMembership]:
        await self.get_user(user_id)
        return await self.membership_repo.get_for_user(user_id)

    async def remove_organization_membership(self, membership_id: uuid.UUID) -> None:
        membership = await self.membership_repo.get_by_id(membership_id)
        if not membership:
            raise NotFoundException(f"Membership record {membership_id} not found.")

        user_id = membership.user_id
        await self.session.delete(membership)

        event = UserLifecycleEvent(
            user_id=user_id,
            event_type="MEMBERSHIP_REVOKED",
            reason="Organizational membership revoked",
            metadata_json={"membership_id": str(membership_id)},
        )
        self.session.add(event)
        await self.session.flush()

    async def get_identity_footprint(self, user_id: uuid.UUID) -> IdentityFootprintResponse:
        user = await self.get_user(user_id)

        std_query = select(Student).where(Student.user_id == user_id)
        student = (await self.session.execute(std_query)).scalars().first()
        student_data = None
        if student:
            student_data = {
                "id": str(student.id),
                "admission_number": student.admission_number,
                "register_number": student.register_number,
                "department_id": str(student.department_id),
                "program_id": str(student.program_id),
                "current_semester": student.current_semester,
                "student_status": student.student_status,
            }

        stf_query = select(Staff).where(Staff.user_id == user_id)
        staff = (await self.session.execute(stf_query)).scalars().first()
        staff_data = None
        if staff:
            staff_data = {
                "id": str(staff.id),
                "staff_id": staff.staff_id,
                "designation": staff.designation,
                "staff_type": staff.staff_type,
                "department_id": str(staff.department_id),
                "school_id": str(staff.school_id) if staff.school_id else None,
                "employment_status": staff.employment_status,
            }

        memberships = await self.membership_repo.get_for_user(user_id)

        return IdentityFootprintResponse(
            user_id=user.id,
            username=user.username,
            email=user.email,
            user_type=user.user_type,
            account_status=user.account_status,
            linked_student=student_data,
            linked_staff=staff_data,
            organization_memberships=[UserOrganizationMembershipResponse.model_validate(m) for m in memberships],
        )

    # --------------------------------------------------------------------------
    # Authentication Foundation (Stage 3.7)
    # --------------------------------------------------------------------------

    async def authenticate(
        self,
        req: LoginRequest,
        ip_address: Optional[str] = None,
    ) -> TokenResponse:
        """
        Authenticates user with username/email and password.
        Handles brute-force protection, lockout triggers, and session token generation.
        """
        now = datetime.now(timezone.utc)
        user = await self.user_repo.get_by_identifier(req.username_or_email)
        if not user:
            raise AuthenticationException("Invalid username, email, or password.")

        # Check account status
        if user.account_status == "PENDING_ACTIVATION":
            raise AuthenticationException("Account is pending activation. Please verify your institutional email first.")
        elif user.account_status == "SUSPENDED":
            raise AuthenticationException("Account has been suspended. Please contact institutional administration.")
        elif user.account_status == "DEACTIVATED":
            raise AuthenticationException("Account has been deactivated.")
        elif user.account_status == "LOCKED":
            if user.locked_until and user.locked_until > now:
                remaining_mins = int((user.locked_until - now).total_seconds() / 60) + 1
                raise AuthenticationException(
                    f"Account is temporarily locked due to excessive failed attempts. Please retry in {remaining_mins} minutes."
                )
            else:
                # Lock window elapsed -> auto unlock
                user.failed_login_attempts = 0
                user.locked_until = None
                user.account_status = "ACTIVE"

        # Verify password
        if not verify_password(req.password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.account_status = "LOCKED"
                user.locked_until = now + timedelta(minutes=15)
                lock_event = UserLifecycleEvent(
                    user_id=user.id,
                    event_type="LOCKED_OUT",
                    reason="Locked out due to 5 consecutive failed login attempts.",
                    metadata_json={"ip_address": ip_address, "device_info": req.device_info},
                )
                self.session.add(lock_event)

            fail_event = UserLifecycleEvent(
                user_id=user.id,
                event_type="LOGIN_FAILED",
                reason="Invalid credentials submitted.",
                metadata_json={"attempt_count": user.failed_login_attempts, "ip_address": ip_address},
            )
            self.session.add(fail_event)
            await self.session.commit()
            raise AuthenticationException("Invalid username, email, or password.")

        # Successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = now

        # Token generation
        user_claims = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "user_type": user.user_type,
        }
        access_token = create_access_token(user_claims)
        refresh_jti = str(uuid.uuid4())
        refresh_token = create_refresh_token({"sub": str(user.id), "jti": refresh_jti})

        # Persist refresh token in DB
        refresh_expires = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_entity = UserRefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            jti=refresh_jti,
            device_info=req.device_info,
            ip_address=ip_address,
            expires_at=refresh_expires,
        )
        self.session.add(refresh_entity)

        # Audit event
        success_event = UserLifecycleEvent(
            user_id=user.id,
            event_type="LOGIN_SUCCESS",
            reason="User authenticated successfully.",
            metadata_json={"ip_address": ip_address, "device_info": req.device_info},
        )
        self.session.add(success_event)
        await self.session.commit()
        fresh_user = await self.user_repo.get_with_profile(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(fresh_user or user),
        )

    async def refresh_tokens(
        self,
        refresh_token_str: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> TokenResponse:
        """
        Validates refresh token, rotates token pair, and preserves active session.
        """
        now = datetime.now(timezone.utc)
        payload = decode_jwt(refresh_token_str)
        if payload.get("type") != "refresh":
            raise AuthenticationException("Invalid token type. Refresh token required.")

        jti = payload.get("jti")
        user_id_str = payload.get("sub")
        if not jti or not user_id_str:
            raise AuthenticationException("Malformed refresh token payload.")

        # Check blacklist
        if await self.revoked_token_repo.is_jti_revoked(jti):
            raise AuthenticationException("Refresh token has been revoked.")

        # Check database record
        token_hash = hash_token(refresh_token_str)
        stored_token = await self.refresh_token_repo.get_active_by_hash(token_hash)
        if not stored_token:
            raise AuthenticationException("Refresh token is expired, revoked, or unrecognized.")

        # Invalidate old refresh token (Token Rotation)
        stored_token.is_revoked = True
        stored_token.revoked_at = now
        stored_token.revoked_reason = "Rotated upon refresh request"

        user = await self.get_user(uuid.UUID(user_id_str))
        if user.account_status != "ACTIVE":
            raise AuthenticationException(f"Account is '{user.account_status}'. Token refresh disallowed.")

        # Issue fresh token pair
        user_claims = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "user_type": user.user_type,
        }
        new_access_token = create_access_token(user_claims)
        new_refresh_jti = str(uuid.uuid4())
        new_refresh_token = create_refresh_token({"sub": str(user.id), "jti": new_refresh_jti})

        # Persist new refresh token
        new_refresh_entity = UserRefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_refresh_token),
            jti=new_refresh_jti,
            device_info=device_info or stored_token.device_info,
            ip_address=ip_address or stored_token.ip_address,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.session.add(new_refresh_entity)

        refresh_event = UserLifecycleEvent(
            user_id=user.id,
            event_type="TOKEN_REFRESH",
            reason="User rotated credentials with valid refresh token.",
            metadata_json={"ip_address": ip_address},
        )
        self.session.add(refresh_event)
        await self.session.commit()
        fresh_user = await self.user_repo.get_with_profile(user.id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(fresh_user or user),
        )

    async def logout(
        self,
        access_token_str: str,
        refresh_token_str: Optional[str] = None,
    ) -> None:
        """
        Invalidates current session: blacklists access token JTI and revokes refresh token.
        """
        now = datetime.now(timezone.utc)
        payload = decode_jwt(access_token_str)
        user_id = uuid.UUID(payload["sub"])
        jti = payload["jti"]
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        # Blacklist access token
        await self.revoked_token_repo.blacklist_token(
            jti=jti,
            user_id=user_id,
            expires_at=exp,
            reason="User logged out",
            token_type="ACCESS",
        )

        # Revoke refresh token if supplied
        if refresh_token_str:
            try:
                ref_payload = decode_jwt(refresh_token_str)
                ref_jti = ref_payload.get("jti")
                ref_exp = datetime.fromtimestamp(ref_payload.get("exp", exp.timestamp()), tz=timezone.utc)
                if ref_jti:
                    await self.revoked_token_repo.blacklist_token(
                        jti=ref_jti,
                        user_id=user_id,
                        expires_at=ref_exp,
                        reason="User logged out",
                        token_type="REFRESH",
                    )
                ref_hash = hash_token(refresh_token_str)
                stored_ref = await self.refresh_token_repo.get_active_by_hash(ref_hash)
                if stored_ref:
                    stored_ref.is_revoked = True
                    stored_ref.revoked_at = now
                    stored_ref.revoked_reason = "Logout"
            except Exception:
                pass

        logout_event = UserLifecycleEvent(
            user_id=user_id,
            event_type="LOGOUT",
            reason="User logged out session.",
        )
        self.session.add(logout_event)
        await self.session.flush()

    async def revoke_token(
        self,
        token_str: str,
        reason: Optional[str] = None,
        performed_by_id: Optional[uuid.UUID] = None,
    ) -> None:
        """
        Revokes an arbitrary access or refresh token immediately.
        """
        now = datetime.now(timezone.utc)
        payload = decode_jwt(token_str)
        user_id = uuid.UUID(payload["sub"])
        jti = payload["jti"]
        token_type = payload.get("type", "access").upper()
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        await self.revoked_token_repo.blacklist_token(
            jti=jti,
            user_id=user_id,
            expires_at=exp,
            reason=reason or "Administrative token revocation",
            token_type=token_type,
        )

        if token_type == "REFRESH":
            stored = await self.refresh_token_repo.get_by_jti(jti)
            if stored:
                stored.is_revoked = True
                stored.revoked_at = now
                stored.revoked_reason = reason or "Manual revocation"

        event = UserLifecycleEvent(
            user_id=user_id,
            event_type="TOKEN_REVOKED",
            performed_by_id=performed_by_id,
            reason=reason or "Token revoked explicitly.",
            metadata_json={"token_type": token_type, "jti": jti},
        )
        self.session.add(event)
        await self.session.flush()

    async def get_current_user_from_token(self, token_str: str) -> User:
        """
        Resolves authenticated User from an active Bearer JWT token.
        Guarantees token is unexpired, signed, unrevoked, and user is active.
        """
        payload = decode_jwt(token_str)
        if payload.get("type") != "access":
            raise AuthenticationException("Invalid token type. Access token required.")

        jti = payload.get("jti")
        if not jti or await self.revoked_token_repo.is_jti_revoked(jti):
            raise AuthenticationException("Authentication token has been revoked. Please log in again.")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationException("Malformed token claims.")

        user = await self.user_repo.get_with_profile(uuid.UUID(user_id_str))
        if not user:
            raise AuthenticationException("User account not found.")

        if user.account_status != "ACTIVE":
            raise AuthenticationException(f"Account is not active (current status: {user.account_status}).")

        return user
