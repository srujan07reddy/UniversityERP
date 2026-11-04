from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.core.logging import logger

# Build Async SQLAlchemy Engine with connection pooling
# Ensure asyncpg dialect is present
db_url = settings.DATABASE_URL

# For SQLite in tests or fallback (supports both sqlite+aiosqlite and postgresql+asyncpg)
is_sqlite = db_url.startswith("sqlite")
is_testing = settings.ENVIRONMENT == "testing"

engine_kwargs = {
    "echo": settings.DB_ECHO,
    "future": True,
}

if is_testing or is_sqlite:
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,
    })

async_engine: AsyncEngine = create_async_engine(db_url, **engine_kwargs)

# Async Session Factory
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for acquiring an async database session outside HTTP request scope
    (e.g., tasks, worker jobs, CLI management commands).
    Guarantees session closure and transaction rollback on error.
    """
    session: AsyncSession = async_session_factory()
    try:
        yield session
    except Exception as exc:
        logger.error(f"Database session rollback triggered by exception: {exc}")
        await session.rollback()
        raise
    finally:
        await session.close()


async def check_database_connection() -> bool:
    """
    Healthcheck probe: executes a lightweight query ('SELECT 1') to verify
    live connectivity to the PostgreSQL cluster.
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning(f"Database connectivity check failed: {exc}")
        return False


async def close_database_connections() -> None:
    """
    Gracefully disposes and closes all pooled connections during application shutdown.
    """
    logger.info("Closing active database connection pools...")
    await async_engine.dispose()
    logger.info("Database connection pools disposed.")
