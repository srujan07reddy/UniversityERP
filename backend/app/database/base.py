import uuid
from datetime import datetime
from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

# Consistent naming convention for all database constraints
# Avoids issues with unnamed constraints across migrations
POSTGRESQL_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base Declarative class for all SQLAlchemy 2.x models in University ERP.
    Configures strict constraint naming convention and automatic tablenames.
    """
    metadata = MetaData(naming_convention=POSTGRESQL_NAMING_CONVENTION)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Default table name is lowercase snake_case of class name
        return cls.__name__.lower()


class UUIDPrimaryKeyMixin:
    """
    Mixin providing standard UUIDv4 primary key.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        sort_order=-100,
    )


class TimestampMixin:
    """
    Mixin providing created_at and updated_at timezone-aware timestamps.
    Automatically managed by the database server and ORM.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        sort_order=900,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        sort_order=901,
    )


class AuditBaseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Abstract base entity combining UUID primary key and audit timestamps.
    All business domain models should inherit from this.
    """
    __abstract__ = True

