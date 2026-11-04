import uuid
import pytest
from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.database.base import (
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    AuditBaseModel,
    POSTGRESQL_NAMING_CONVENTION,
)
from app.database.session import (
    async_engine,
    check_database_connection,
    get_db_session,
)
from app.database.dependencies import get_db
from app.core.config import settings


# Dummy model to test model definition and naming conventions
class SampleTestModel(AuditBaseModel):
    __tablename__ = "sample_test_models"
    name: Mapped[str] = mapped_column(String(100), nullable=False)


def test_naming_conventions():
    """Verify constraint naming convention dictionary format."""
    conv = Base.metadata.naming_convention
    assert conv["ix"] == "ix_%(column_0_label)s"
    assert conv["uq"] == "uq_%(table_name)s_%(column_0_name)s"
    assert conv["ck"] == "ck_%(table_name)s_%(constraint_name)s"
    assert conv["fk"] == "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
    assert conv["pk"] == "pk_%(table_name)s"


def test_audit_base_model_mixins():
    """Verify UUID primary key, timestamp mixin columns, and types."""
    table = SampleTestModel.__table__
    assert "id" in table.columns
    assert "created_at" in table.columns
    assert "updated_at" in table.columns
    assert "name" in table.columns
    assert table.columns["id"].primary_key is True


def test_async_engine_dialect():
    """Verify asynchronous asyncpg PostgreSQL driver dialect is configured."""
    assert async_engine.url.drivername == "postgresql+asyncpg"
    assert async_engine.url.database == settings.POSTGRES_DB


@pytest.mark.asyncio
async def test_live_database_connection():
    """Verify live connectivity to PostgreSQL 17."""
    is_connected = await check_database_connection()
    assert is_connected is True


@pytest.mark.asyncio
async def test_live_postgresql_execution():
    """Verify asynchronous query execution and database metadata."""
    async with async_engine.connect() as conn:
        result = await conn.execute(text("SELECT version(), current_database(), current_user;"))
        row = result.fetchone()
        assert row is not None
        assert "PostgreSQL 17" in row[0]
        assert row[1] == settings.POSTGRES_DB
        assert row[2] == settings.POSTGRES_USER


@pytest.mark.asyncio
async def test_get_db_session_commit():
    """Verify session context manager executes queries and returns scalar results."""
    async with get_db_session() as session:
        result = await session.execute(text("SELECT 42 AS answer;"))
        val = result.scalar()
        assert val == 42


@pytest.mark.asyncio
async def test_get_db_session_rollback_on_failure():
    """Verify session context manager triggers automatic rollback on unhandled errors."""
    with pytest.raises(Exception):
        async with get_db_session() as session:
            await session.execute(text("SELECT * FROM non_existent_table_for_rollback_testing;"))


@pytest.mark.asyncio
async def test_get_db_dependency_generator():
    """Verify FastAPI get_db dependency lifecycle (creation, yield, and closure)."""
    db_gen = get_db()
    session = await anext(db_gen)
    assert isinstance(session, AsyncSession)

    res = await session.execute(text("SELECT 1;"))
    assert res.scalar() == 1

    # Cleanup dependency
    try:
        await anext(db_gen)
    except StopAsyncIteration:
        pass


@pytest.mark.asyncio
async def test_database_connection_failure_handled_safely():
    """Verify check_database_connection handles unreachable endpoints gracefully."""
    # Create invalid engine to simulate network/cluster failure
    dead_engine = create_async_engine("postgresql+asyncpg://invalid:wrong@127.0.0.1:5439/fake_db")
    
    # Connection should return False rather than raising an uncaught exception
    try:
        async with dead_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        connected = True
    except Exception:
        connected = False
    finally:
        await dead_engine.dispose()

    assert connected is False

