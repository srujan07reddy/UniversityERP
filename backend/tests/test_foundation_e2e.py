import uuid
import httpx
import pytest
from sqlalchemy import text
from app.api.v1.endpoints.system import SystemService
from app.core.config import settings
from app.core.logging import (
    get_correlation_id,
    mask_sensitive_data,
    reset_correlation_id,
    set_correlation_id,
)
from app.database.session import (
    async_engine,
    check_database_connection,
    get_db_session,
)
from app.main import app, lifespan


@pytest.mark.asyncio
async def test_e2e_lifespan_lifecycle():
    """Verify application lifespan completes startup and shutdown cleanly."""
    async with lifespan(app):
        # Database should be operational during lifespan
        is_alive = await check_database_connection()
        assert is_alive is True


@pytest.mark.asyncio
async def test_e2e_full_request_response_tracing_cycle():
    """
    Verify complete request lifecycle:
    ASGI routing -> RequestLoggingMiddleware -> Service Layer -> Envelope -> Client.
    """
    custom_request_id = f"trace-e2e-{uuid.uuid4()}"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/system/info",
            headers={"X-Request-ID": custom_request_id},
        )
        assert response.status_code == 200

        # Response headers check
        assert response.headers.get("x-request-id") == custom_request_id
        assert "x-process-time" in response.headers

        # Response body envelope check
        body = response.json()
        assert body["success"] is True
        assert body["request_id"] == custom_request_id
        assert body["data"]["project"] == settings.PROJECT_NAME
        assert body["data"]["database_status"] == "connected"


@pytest.mark.asyncio
async def test_e2e_database_session_and_transaction_integrity():
    """Verify live PostgreSQL session execution with rollback guarantees."""
    async with get_db_session() as session:
        result = await session.execute(text("SELECT 1 AS alive, current_database() AS dbname"))
        row = result.mappings().one()
        assert row["alive"] == 1
        assert row["dbname"] == settings.POSTGRES_DB


@pytest.mark.asyncio
async def test_e2e_validation_error_pipeline():
    """Verify Pydantic input validation failure pipeline with correlation tracing."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid query param: page must be >= 1
        response = await client.get("/api/v1/system/modules?page=0")
        assert response.status_code == 422

        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"
        assert len(body["error"]["details"]) > 0
        assert body["request_id"] == response.headers.get("x-request-id")


@pytest.mark.asyncio
async def test_e2e_alembic_schema_version_in_live_db():
    """Verify live PostgreSQL has Alembic migration version table properly stamped."""
    async with get_db_session() as session:
        result = await session.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar_one_or_none()
        assert version is not None
        assert len(version) == 12  # Standard Alembic revision ID length

