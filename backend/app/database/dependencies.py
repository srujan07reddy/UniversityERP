from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import async_session_factory
from app.core.logging import logger


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI request-scoped dependency providing an isolated AsyncSession.
    Guarantees:
      - A fresh, request-isolated session is provided.
      - Automatic rollback on any unhandled exception during request processing.
      - Guaranteed session closure on completion.
      - Zero cross-request session leakage.
    """
    session: AsyncSession = async_session_factory()
    try:
        yield session
    except Exception as exc:
        logger.error(f"Rolling back request database transaction due to: {exc}")
        await session.rollback()
        raise
    finally:
        await session.close()

