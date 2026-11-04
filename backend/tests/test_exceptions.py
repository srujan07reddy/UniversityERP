import pytest
import httpx
from sqlalchemy.exc import IntegrityError, DBAPIError
from app.main import app
from app.core.exceptions import (
    NotFoundException,
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    ValidationException,
    BadRequestException,
    DatabaseException,
)

# Register test routes on app for testing exception handlers
@app.get("/test-err/not-found", include_in_schema=False)
def err_not_found():
    raise NotFoundException("Student profile not found")

@app.get("/test-err/auth", include_in_schema=False)
def err_auth():
    raise AuthenticationException("JWT signature has expired")

@app.get("/test-err/forbidden", include_in_schema=False)
def err_forbidden():
    raise AuthorizationException("Dean approval role required")

@app.get("/test-err/conflict", include_in_schema=False)
def err_conflict():
    raise ConflictException("Roll number 2026-CS-001 already assigned")

@app.get("/test-err/bad-request", include_in_schema=False)
def err_bad_request():
    raise BadRequestException("Malformed query parameter format")

@app.get("/test-err/db-exception", include_in_schema=False)
def err_db():
    raise DatabaseException("Connection pool exhaustion")

@app.get("/test-err/integrity", include_in_schema=False)
def err_integrity():
    raise IntegrityError("INSERT INTO students...", {}, Exception("violates foreign key constraint"))

@app.get("/test-err/dbapi", include_in_schema=False)
def err_dbapi():
    raise DBAPIError("SELECT ...", {}, Exception("network socket disconnect"))

@app.get("/test-err/unhandled-crash", include_in_schema=False)
def err_unhandled():
    raise RuntimeError("Critical leak: secret_database_password_99999 at line 42")


@pytest.mark.asyncio
async def test_not_found_exception_envelope():
    """Verify 404 NotFoundException maps to standardized error envelope."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/test-err/not-found")
        assert response.status_code == 404
        payload = response.json()

        assert payload["success"] is False
        assert payload["error"]["code"] == "RESOURCE_NOT_FOUND"
        assert payload["error"]["message"] == "Student profile not found"
        assert payload["error"]["details"] == []
        assert "request_id" in payload


@pytest.mark.asyncio
async def test_authentication_exception_envelope():
    """Verify 401 AuthenticationException maps to standardized error envelope."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/test-err/auth")
        assert response.status_code == 401
        payload = response.json()

        assert payload["success"] is False
        assert payload["error"]["code"] == "AUTHENTICATION_REQUIRED"
        assert payload["error"]["message"] == "JWT signature has expired"


@pytest.mark.asyncio
async def test_authorization_exception_envelope():
    """Verify 403 AuthorizationException maps to standardized error envelope."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/test-err/forbidden")
        assert response.status_code == 403
        payload = response.json()

        assert payload["success"] is False
        assert payload["error"]["code"] == "PERMISSION_DENIED"
        assert payload["error"]["message"] == "Dean approval role required"


@pytest.mark.asyncio
async def test_conflict_exception_envelope():
    """Verify 409 ConflictException maps to standardized error envelope."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/test-err/conflict")
        assert response.status_code == 409
        payload = response.json()

        assert payload["success"] is False
        assert payload["error"]["code"] == "RESOURCE_CONFLICT"
        assert "Roll number" in payload["error"]["message"]


@pytest.mark.asyncio
async def test_bad_request_exception_envelope():
    """Verify 400 BadRequestException maps to standardized error envelope."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/test-err/bad-request")
        assert response.status_code == 400
        payload = response.json()

        assert payload["success"] is False
        assert payload["error"]["code"] == "BAD_REQUEST"


@pytest.mark.asyncio
async def test_database_integrity_error_safety():
    """Verify SQLAlchemy IntegrityError returns 409 without leaking raw SQL."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/test-err/integrity")
        assert response.status_code == 409
        payload = response.json()

        assert payload["success"] is False
        assert payload["error"]["code"] == "RESOURCE_CONFLICT"
        # Never leak raw SQL query
        assert "INSERT INTO" not in payload["error"]["message"]


@pytest.mark.asyncio
async def test_unhandled_crash_safe_masking():
    """Verify unhandled exceptions return 500 without leaking stack traces or internal secrets."""
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/test-err/unhandled-crash")
        assert response.status_code == 500
        payload = response.json()

        assert payload["success"] is False
        assert payload["error"]["code"] == "INTERNAL_SERVER_ERROR"
        # Secret must never appear in response
        assert "secret_database_password_99999" not in payload["error"]["message"]
        assert "line 42" not in payload["error"]["message"]


@pytest.mark.asyncio
async def test_pydantic_validation_error_envelope():
    """Verify FastAPI / Pydantic validation error returns 422 with structured field details."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/system/modules?page=-99&page_size=999")
        assert response.status_code == 422
        payload = response.json()

        assert payload["success"] is False
        assert payload["error"]["code"] == "VALIDATION_ERROR"
        assert len(payload["error"]["details"]) >= 1

        fields = [d["field"] for d in payload["error"]["details"]]
        assert "page" in fields or "page_size" in fields


@pytest.mark.asyncio
async def test_starlette_404_routing_error():
    """Verify route not found (Starlette 404) returns standardized error envelope."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/completely/nonexistent/path/999")
        assert response.status_code == 404
        payload = response.json()

        assert payload["success"] is False
        assert payload["error"]["code"] == "RESOURCE_NOT_FOUND"
        assert payload["error"]["message"] == "Not Found"


@pytest.mark.asyncio
async def test_request_id_in_error_envelope():
    """Verify caller-provided X-Request-ID appears inside the error envelope and header."""
    custom_trace_id = "trace-error-verify-554433"
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/test-err/not-found",
            headers={"X-Request-ID": custom_trace_id},
        )
        assert response.status_code == 404
        payload = response.json()

        assert payload["request_id"] == custom_trace_id
        assert response.headers.get("x-request-id") == custom_trace_id
