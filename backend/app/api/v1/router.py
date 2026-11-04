from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.endpoints.system import router as system_router

api_v1_router = APIRouter()

# Register core platform and infrastructure endpoints
api_v1_router.include_router(health_router)
api_v1_router.include_router(system_router)

# Future domain routers will be registered here cleanly:
# api_v1_router.include_router(identity_router, prefix="/auth", tags=["Authentication"])
# api_v1_router.include_router(organization_router, prefix="/organization", tags=["Organization"])
