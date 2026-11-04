from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.endpoints.system import router as system_router
from app.platform.organization.router import router as organization_router
from app.platform.identity.router import router as identity_router
from app.platform.identity.auth_router import router as auth_router
from app.domains.students.router import router as students_router
from app.domains.staff.router import router as staff_router

api_v1_router = APIRouter()

# Register core platform and infrastructure endpoints
api_v1_router.include_router(health_router)
api_v1_router.include_router(system_router)
api_v1_router.include_router(organization_router)
api_v1_router.include_router(identity_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(students_router)
api_v1_router.include_router(staff_router)
