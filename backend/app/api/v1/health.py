from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from app.core.config import settings
from app.database.session import check_database_connection

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    environment: str = Field(..., examples=["development"])
    version: str = Field(..., examples=["0.1.0"])
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    services: Dict[str, Any] = Field(default_factory=dict)


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Health Probe",
    description="Returns current operational status, environment, version, and database connectivity.",
)
async def get_health() -> HealthResponse:
    db_ok = await check_database_connection()
    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        services={
            "api": "operational",
            "database": "connected" if db_ok else "unreachable",
        },
    )
