import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Sequence, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.platform.identity.models import (
    RevokedToken,
    User,
    UserLifecycleEvent,
    UserOrganizationMembership,
    UserProfile,
    UserRecoveryToken,
    UserRefreshToken,
)
from app.platform.identity.schemas import (
    UserCreate,
    UserOrganizationMembershipCreate,
    UserProfileCreate,
    UserProfileUpdate,
    UserUpdate,
)
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(self.model).options(selectinload(self.model.profile)).where(self.model.username == username.strip())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(self.model).options(selectinload(self.model.profile)).where(self.model.email == email.strip().lower())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_phone(self, phone: str) -> Optional[User]:
        query = select(self.model).options(selectinload(self.model.profile)).where(self.model.phone == phone.strip())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_identifier(self, identifier: str) -> Optional[User]:
        """Find user by username, institutional email, or phone."""
        clean_id = identifier.strip()
        query = (
            select(self.model)
            .options(selectinload(self.model.profile))
            .where(
                or_(
                    self.model.username == clean_id,
                    self.model.email == clean_id.lower(),
                    self.model.phone == clean_id,
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_with_profile(self, user_id: uuid.UUID) -> Optional[User]:
        query = select(self.model).options(selectinload(self.model.profile)).where(self.model.id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()


class UserProfileRepository(BaseRepository[UserProfile, UserProfileCreate, UserProfileUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserProfile, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()


class UserRecoveryTokenRepository(BaseRepository[UserRecoveryToken, Any, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserRecoveryToken, session)

    async def get_active_token(self, token_hash: str, token_type: str) -> Optional[UserRecoveryToken]:
        now = datetime.now(timezone.utc)
        query = (
            select(self.model)
            .where(
                self.model.token_hash == token_hash,
                self.model.token_type == token_type,
                self.model.used_at.is_(None),
                self.model.expires_at > now,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()


class UserLifecycleEventRepository(BaseRepository[UserLifecycleEvent, Any, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserLifecycleEvent, session)

    async def get_for_user(self, user_id: uuid.UUID) -> Sequence[UserLifecycleEvent]:
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_events(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        user_id: Optional[uuid.UUID] = None,
        event_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Tuple[Sequence[UserLifecycleEvent], int]:
        query = select(self.model)
        count_query = select(func.count(self.model.id))

        filters = []
        if user_id:
            filters.append(self.model.user_id == user_id)
        if event_type:
            filters.append(self.model.event_type == event_type.strip().upper())
        if from_date:
            filters.append(self.model.created_at >= from_date)
        if to_date:
            filters.append(self.model.created_at <= to_date)

        for f in filters:
            query = query.where(f)
            count_query = count_query.where(f)

        total_res = await self.session.execute(count_query)
        total = total_res.scalar() or 0

        query = query.order_by(self.model.created_at.desc()).offset(offset).limit(limit)
        items_res = await self.session.execute(query)
        items = items_res.scalars().all()

        return items, total


class UserOrganizationMembershipRepository(BaseRepository[UserOrganizationMembership, UserOrganizationMembershipCreate, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserOrganizationMembership, session)

    async def get_for_user(self, user_id: uuid.UUID) -> Sequence[UserOrganizationMembership]:
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.is_primary.desc(), self.model.effective_from.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_user_and_unit(
        self, user_id: uuid.UUID, unit_id: uuid.UUID, membership_type: str
    ) -> Optional[UserOrganizationMembership]:
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.unit_id == unit_id,
            self.model.membership_type == membership_type.strip().upper(),
        )
        result = await self.session.execute(query)
        return result.scalars().first()


class UserRefreshTokenRepository(BaseRepository[UserRefreshToken, Any, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserRefreshToken, session)

    async def get_active_by_hash(self, token_hash: str) -> Optional[UserRefreshToken]:
        now = datetime.now(timezone.utc)
        query = select(self.model).where(
            self.model.token_hash == token_hash,
            self.model.is_revoked.is_(False),
            self.model.expires_at > now,
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_jti(self, jti: str) -> Optional[UserRefreshToken]:
        query = select(self.model).where(self.model.jti == jti)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def revoke_all_for_user(self, user_id: uuid.UUID, reason: Optional[str] = None) -> int:
        now = datetime.now(timezone.utc)
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.is_revoked.is_(False),
        )
        result = await self.session.execute(query)
        tokens = result.scalars().all()
        for t in tokens:
            t.is_revoked = True
            t.revoked_at = now
            t.revoked_reason = reason or "User session revoked all devices"
        return len(tokens)


class RevokedTokenRepository(BaseRepository[RevokedToken, Any, Any]):
    def __init__(self, session: AsyncSession):
        super().__init__(RevokedToken, session)

    async def is_jti_revoked(self, jti: str) -> bool:
        now = datetime.now(timezone.utc)
        query = select(self.model).where(
            self.model.jti == jti,
            self.model.expires_at > now,
        )
        result = await self.session.execute(query)
        return result.scalars().first() is not None

    async def blacklist_token(
        self,
        jti: str,
        user_id: uuid.UUID,
        expires_at: datetime,
        reason: Optional[str] = None,
        token_type: str = "ACCESS",
    ) -> RevokedToken:
        existing = await self.is_jti_revoked(jti)
        if existing:
            return None  # type: ignore[return-value]
        record = RevokedToken(
            jti=jti,
            user_id=user_id,
            token_type=token_type,
            expires_at=expires_at,
            reason=reason or "Logout or manual revocation",
        )
        self.session.add(record)
        return record
