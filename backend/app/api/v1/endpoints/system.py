import os
import platform
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import get_correlation_id
from app.database.session import check_database_connection
from app.schemas.response import (
    APIResponse,
    PaginatedResponse,
    PaginationMetadata,
    PaginationParams,
)

router = APIRouter(prefix="/system", tags=["System Architecture"])


class SystemInfo(BaseModel):
    project: str = Field(..., description="Institutional project name")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Runtime environment")
    python_version: str = Field(..., description="Python runtime version")
    platform: str = Field(..., description="Host OS platform")
    database_status: str = Field(..., description="Live PostgreSQL connectivity")
    timestamp: datetime = Field(..., description="UTC server timestamp")


class ModuleInfo(BaseModel):
    id: str
    name: str
    category: str
    status: str


# Service implementing business logic decoupled from routing
class SystemService:
    @staticmethod
    async def get_system_info() -> SystemInfo:
        db_ok = await check_database_connection()
        return SystemInfo(
            project=settings.PROJECT_NAME,
            version=settings.VERSION,
            environment=settings.ENVIRONMENT,
            python_version=platform.python_version(),
            platform=f"{platform.system()} {platform.release()}",
            database_status="connected" if db_ok else "unreachable",
            timestamp=datetime.now(timezone.utc),
        )

    @staticmethod
    def get_registered_modules(pagination: PaginationParams) -> tuple[List[ModuleInfo], PaginationMetadata]:
        all_modules = [
            ModuleInfo(id="identity", name="Identity & Access Management", category="Platform", status="active"),
            ModuleInfo(id="access_control", name="RBAC & Permission Engine", category="Platform", status="active"),
            ModuleInfo(id="organization", name="Institutional Structure", category="Platform", status="active"),
            ModuleInfo(id="workflows", name="Governance & Workflow Engine", category="Platform", status="active"),
            ModuleInfo(id="audit", name="Immutable Audit Logs", category="Platform", status="active"),
            ModuleInfo(id="notifications", name="Event Notification Dispatcher", category="Platform", status="active"),
            ModuleInfo(id="documents", name="Document Storage & Verification", category="Platform", status="active"),
            ModuleInfo(id="configuration", name="Dynamic Configuration Engine", category="Platform", status="active"),
            ModuleInfo(id="students", name="Student Lifecycle Management", category="Domain", status="scaffolded"),
            ModuleInfo(id="staff", name="Employee & Faculty Workload", category="Domain", status="scaffolded"),
            ModuleInfo(id="admissions", name="Admissions & Enrollment", category="Domain", status="scaffolded"),
            ModuleInfo(id="academics", name="Courses, Programmes & Curricula", category="Domain", status="scaffolded"),
            ModuleInfo(id="attendance", name="Student & Staff Attendance", category="Domain", status="scaffolded"),
            ModuleInfo(id="examinations", name="Examinations, Grading & Results", category="Domain", status="scaffolded"),
            ModuleInfo(id="finance", name="Fee Invoicing & Payments", category="Domain", status="scaffolded"),
            ModuleInfo(id="placements", name="Corporate Placements & Drives", category="Domain", status="scaffolded"),
            ModuleInfo(id="mentorship", name="Faculty Mentorship", category="Domain", status="scaffolded"),
            ModuleInfo(id="wellbeing", name="Student Wellbeing (Isolated)", category="Domain", status="scaffolded"),
            ModuleInfo(id="communications", name="Institutional Communications", category="Domain", status="scaffolded"),
            ModuleInfo(id="library", name="Library & Catalog Management", category="Domain", status="scaffolded"),
            ModuleInfo(id="hostel", name="Hostel & Room Allocation", category="Domain", status="scaffolded"),
            ModuleInfo(id="transport", name="Transport Routes & Tracking", category="Domain", status="scaffolded"),
            ModuleInfo(id="research", name="Research & Grant Administration", category="Domain", status="scaffolded"),
        ]

        total = len(all_modules)
        start = pagination.offset
        end = start + pagination.limit
        sliced = all_modules[start:end]

        metadata = PaginationMetadata.create(
            page=pagination.page,
            page_size=pagination.page_size,
            total_items=total,
        )
        return sliced, metadata


@router.get(
    "/info",
    response_model=APIResponse[SystemInfo],
    status_code=status.HTTP_200_OK,
    summary="System Information",
    description="Returns detailed platform metadata wrapped in a standard API envelope.",
)
async def get_system_info(request: Request) -> APIResponse[SystemInfo]:
    info = await SystemService.get_system_info()
    return APIResponse(
        success=True,
        data=info,
        message="System runtime information retrieved successfully.",
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )


@router.get(
    "/modules",
    response_model=PaginatedResponse[ModuleInfo],
    status_code=status.HTTP_200_OK,
    summary="Registered ERP Modules",
    description="Returns a paginated collection of registered platform and domain modules.",
)
def get_modules(
    request: Request,
    pagination: PaginationParams = Depends(),
) -> PaginatedResponse[ModuleInfo]:
    items, metadata = SystemService.get_registered_modules(pagination)
    return PaginatedResponse(
        success=True,
        data=items,
        pagination=metadata,
        request_id=request.headers.get("X-Request-ID") or get_correlation_id(),
    )

