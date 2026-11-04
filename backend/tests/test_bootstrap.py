import pytest
import httpx
from app.main import app
from app.core.config import settings


@pytest.mark.asyncio
async def test_root_redirect_to_docs():
    """Verify that root / redirects to Swagger documentation (/docs)."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/docs"


@pytest.mark.asyncio
async def test_root_health_probe():
    """Verify root /health endpoint and middleware latency headers."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["project"] == settings.PROJECT_NAME
        assert data["version"] == settings.VERSION
        assert data["environment"] == settings.ENVIRONMENT

        # Middleware verification
        assert "x-process-time" in response.headers
        assert "x-request-id" in response.headers
        assert data.get("database") in ("connected", "unreachable")


@pytest.mark.asyncio
async def test_api_v1_health_probe():
    """Verify versioned /api/v1/health endpoint and schema."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"{settings.API_V1_PREFIX}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert data["version"] == settings.VERSION
        assert data["environment"] == settings.ENVIRONMENT
        assert "timestamp" in data
        assert data["services"]["api"] == "operational"
        assert data["services"]["database"] in ("connected", "unreachable")


@pytest.mark.asyncio
async def test_openapi_json_schema():
    """Verify OpenAPI 3.x schema generation and metadata."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == settings.PROJECT_NAME
        assert schema["info"]["version"] == settings.VERSION
        assert f"{settings.API_V1_PREFIX}/health" in schema["paths"]


@pytest.mark.asyncio
async def test_swagger_and_redoc_ui_accessible():
    """Verify Swagger UI and ReDoc HTML endpoints are served."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        r_docs = await client.get("/docs")
        assert r_docs.status_code == 200
        assert "swagger-ui" in r_docs.text.lower()

        r_redoc = await client.get("/redoc")
        assert r_redoc.status_code == 200
        assert "redoc" in r_redoc.text.lower()


@pytest.mark.asyncio
async def test_custom_request_id_propagation():
    """Verify custom X-Request-ID header is preserved and returned."""
    custom_id = "test-custom-trace-id-12345"
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health", headers={"X-Request-ID": custom_id})
        assert response.status_code == 200
        assert response.headers["x-request-id"] == custom_id

