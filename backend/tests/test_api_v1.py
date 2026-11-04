import pytest
import httpx
from app.main import app
from app.core.config import settings
from app.schemas.response import APIResponse, PaginatedResponse, PaginationMetadata


@pytest.mark.asyncio
async def test_system_info_endpoint_envelope():
    """Verify GET /api/v1/system/info returns standard APIResponse envelope."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"{settings.API_V1_PREFIX}/system/info")
        assert response.status_code == 200
        payload = response.json()

        # Envelope verification
        assert payload["success"] is True
        assert "data" in payload
        assert "message" in payload
        assert "request_id" in payload

        # Payload data verification
        data = payload["data"]
        assert data["project"] == settings.PROJECT_NAME
        assert data["version"] == settings.VERSION
        assert data["environment"] == settings.ENVIRONMENT
        assert data["database_status"] in ("connected", "unreachable")
        assert "python_version" in data
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_system_modules_paginated_response():
    """Verify GET /api/v1/system/modules returns standard PaginatedResponse envelope."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Request page 1 with page_size 5
        response = await client.get(f"{settings.API_V1_PREFIX}/system/modules?page=1&page_size=5")
        assert response.status_code == 200
        payload = response.json()

        # Paginated envelope verification
        assert payload["success"] is True
        assert isinstance(payload["data"], list)
        assert len(payload["data"]) == 5
        assert "pagination" in payload

        # Pagination metadata verification
        p = payload["pagination"]
        assert p["page"] == 1
        assert p["page_size"] == 5
        assert p["total_items"] == 23
        assert p["total_pages"] == 5
        assert p["has_next"] is True
        assert p["has_previous"] is False


@pytest.mark.asyncio
async def test_system_modules_pagination_navigation():
    """Verify navigating to page 2 and edge pagination boundaries."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Request page 2 with page_size 10
        response = await client.get(f"{settings.API_V1_PREFIX}/system/modules?page=2&page_size=10")
        assert response.status_code == 200
        payload = response.json()

        p = payload["pagination"]
        assert p["page"] == 2
        assert p["page_size"] == 10
        assert p["has_previous"] is True
        assert p["has_next"] is True
        assert len(payload["data"]) == 10


@pytest.mark.asyncio
async def test_system_modules_invalid_pagination():
    """Verify 422 Unprocessable Entity for invalid pagination parameters."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # page < 1 should fail validation
        r1 = await client.get(f"{settings.API_V1_PREFIX}/system/modules?page=0")
        assert r1.status_code == 422

        # page_size > 100 should fail validation
        r2 = await client.get(f"{settings.API_V1_PREFIX}/system/modules?page_size=200")
        assert r2.status_code == 422


@pytest.mark.asyncio
async def test_request_id_in_envelope():
    """Verify caller-provided X-Request-ID appears inside the response envelope and header."""
    custom_trace_id = "trace-erp-arch-98765"
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"{settings.API_V1_PREFIX}/system/info",
            headers={"X-Request-ID": custom_trace_id},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["request_id"] == custom_trace_id
        assert response.headers.get("x-request-id") == custom_trace_id


@pytest.mark.asyncio
async def test_openapi_schema_contains_v1_endpoints():
    """Verify OpenAPI documentation accurately indexes all v1 endpoints and tags."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()

        assert f"{settings.API_V1_PREFIX}/system/info" in schema["paths"]
        assert f"{settings.API_V1_PREFIX}/system/modules" in schema["paths"]
        assert f"{settings.API_V1_PREFIX}/health" in schema["paths"]

