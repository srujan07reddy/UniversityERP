from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import logger, setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.api.v1.router import api_v1_router
from app.database.session import check_database_connection, close_database_connections


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application startup and shutdown lifecycle management.
    Handles logging initialization, database connectivity verification, and connection teardown.
    """
    # Startup actions
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} (v{settings.VERSION})")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Debug: {settings.DEBUG} | Log Level: {settings.LOG_LEVEL} | Log Format: {settings.LOG_FORMAT}")

    # Check database connectivity
    db_ok = await check_database_connection()
    if db_ok:
        logger.info("Database connectivity check: OK (PostgreSQL connected)")
    else:
        logger.warning("Database connectivity check: FAILED (Database offline or unreachable; continuing startup in degraded mode)")
    
    yield
    
    # Shutdown actions
    await close_database_connections()
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


def create_application() -> FastAPI:
    """
    FastAPI Application Factory.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="University ERP — Modular Monolith REST API backend.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Cross-Origin Resource Sharing (CORS)
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Request latency, correlation & access logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Register standardized global exception handlers
    setup_exception_handlers(app)

    # Root endpoint: redirect to Swagger docs for developer convenience
    @app.get("/", include_in_schema=False)
    async def root_redirect():
        return RedirectResponse(url="/docs")

    # Global health check probe for load balancers and orchestrators
    @app.get(
        "/health",
        status_code=status.HTTP_200_OK,
        tags=["System"],
        summary="Root Health Check",
    )
    async def root_health():
        db_ok = await check_database_connection()
        return {
            "status": "healthy" if db_ok else "degraded",
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "connected" if db_ok else "unreachable",
        }

    # Mount API v1 router
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
