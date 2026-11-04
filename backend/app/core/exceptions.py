import uuid
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import DBAPIError, IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import get_correlation_id, logger


# ==============================================================================
# Error Response Schemas
# ==============================================================================

class ErrorDetail(BaseModel):
    code: str = Field(..., description="Standardized error category code")
    message: str = Field(..., description="Human-readable error explanation")
    details: Optional[List[Any]] = Field(default_factory=list, description="Granular error breakdowns")


class ErrorResponse(BaseModel):
    """
    Standardized institutional error response envelope.
    All errors across the ERP adhere strictly to this schema.
    """
    success: bool = Field(default=False, description="Always false for error states")
    error: ErrorDetail = Field(..., description="Structured error payload")
    request_id: Optional[str] = Field(default=None, description="Correlation identifier for distributed tracing")


# ==============================================================================
# Application Exception Hierarchy
# ==============================================================================

class BaseAppException(Exception):
    """Base class for all university ERP application exceptions."""
    def __init__(
        self,
        message: str = "An unexpected error occurred",
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[List[Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []


class ValidationException(BaseAppException):
    """Raised when request payload or business state fails validation."""
    def __init__(self, message: str = "Invalid request data", details: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class AuthenticationException(BaseAppException):
    """Raised when authentication credentials are missing or invalid."""
    def __init__(self, message: str = "Authentication required or credentials invalid", details: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_REQUIRED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationException(BaseAppException):
    """Raised when the authenticated principal lacks required RBAC permissions or scope."""
    def __init__(self, message: str = "Permission denied for this institutional resource", details: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class NotFoundException(BaseAppException):
    """Raised when requested entity or resource is not found."""
    def __init__(self, message: str = "The requested institutional resource was not found", details: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class ConflictException(BaseAppException):
    """Raised on state conflict, unique constraint violation, or duplicate record."""
    def __init__(self, message: str = "Resource state conflict or duplicate detected", details: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            code="RESOURCE_CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class BadRequestException(BaseAppException):
    """Raised on malformed or invalid request syntax."""
    def __init__(self, message: str = "Bad or malformed request", details: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            code="BAD_REQUEST",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class DatabaseException(BaseAppException):
    """Raised when database operations encounter an internal failure."""
    def __init__(self, message: str = "Database operation failed", details: Optional[List[Any]] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


# ==============================================================================
# Helper to extract Request ID
# ==============================================================================

def get_request_id(request: Request) -> str:
    return request.headers.get("X-Request-ID") or get_correlation_id() or str(uuid.uuid4())


# ==============================================================================
# Global Exception Handlers Setup
# ==============================================================================

def setup_exception_handlers(app: FastAPI) -> None:
    """
    Registers global exception handlers on the FastAPI application instance.
    Guarantees:
      - 100% of errors return the standard ErrorResponse envelope.
      - HTTP status codes are preserved accurately.
      - Internal stack traces, raw SQL queries, and secrets are never exposed.
      - Request IDs are propagated in all error responses for observability.
    """

    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
        req_id = get_request_id(request)
        logger.warning(f"[{req_id}] Application error ({exc.code}): {exc.message}")
        content = ErrorResponse(
            success=False,
            error=ErrorDetail(code=exc.code, message=exc.message, details=exc.details),
            request_id=req_id,
        ).model_dump()
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        req_id = get_request_id(request)
        clean_details = []
        for err in exc.errors():
            loc = err.get("loc", ())
            field = ".".join(str(x) for x in loc if x not in ("body", "query", "path")) or "payload"
            clean_details.append({
                "field": field,
                "message": err.get("msg", "Invalid value"),
                "type": err.get("type", "value_error"),
            })

        logger.info(f"[{req_id}] Request validation failed: {clean_details}")
        content = ErrorResponse(
            success=False,
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Request input validation failed. Check details.",
                details=clean_details,
            ),
            request_id=req_id,
        ).model_dump()
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=content)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        req_id = get_request_id(request)
        # Map common status codes to standardized codes
        code_map = {
            status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
            status.HTTP_401_UNAUTHORIZED: "AUTHENTICATION_REQUIRED",
            status.HTTP_403_FORBIDDEN: "PERMISSION_DENIED",
            status.HTTP_404_NOT_FOUND: "RESOURCE_NOT_FOUND",
            status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
            status.HTTP_409_CONFLICT: "RESOURCE_CONFLICT",
            status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
            status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMIT_EXCEEDED",
        }
        err_code = code_map.get(exc.status_code, "HTTP_ERROR")
        logger.warning(f"[{req_id}] HTTP {exc.status_code} ({err_code}): {exc.detail}")

        content = ErrorResponse(
            success=False,
            error=ErrorDetail(code=err_code, message=str(exc.detail), details=[]),
            request_id=req_id,
        ).model_dump()
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        req_id = get_request_id(request)
        logger.error(f"[{req_id}] Database integrity constraint violation: {exc}")
        # Never leak raw DB constraint or table internals to the client
        content = ErrorResponse(
            success=False,
            error=ErrorDetail(
                code="RESOURCE_CONFLICT",
                message="A data constraint conflict occurred (e.g., duplicate record or invalid reference).",
                details=[],
            ),
            request_id=req_id,
        ).model_dump()
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=content)

    @app.exception_handler(DBAPIError)
    async def dbapi_error_handler(request: Request, exc: DBAPIError) -> JSONResponse:
        req_id = get_request_id(request)
        logger.error(f"[{req_id}] Database driver error: {exc}")
        content = ErrorResponse(
            success=False,
            error=ErrorDetail(
                code="DATABASE_ERROR",
                message="A database communication error occurred. Please try again later.",
                details=[],
            ),
            request_id=req_id,
        ).model_dump()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        req_id = get_request_id(request)
        logger.error(f"[{req_id}] SQLAlchemy ORM error: {exc}")
        content = ErrorResponse(
            success=False,
            error=ErrorDetail(
                code="DATABASE_ERROR",
                message="A database processing error occurred.",
                details=[],
            ),
            request_id=req_id,
        ).model_dump()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)

    @app.exception_handler(500)
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = get_request_id(request)
        logger.exception(f"[{req_id}] Unhandled server exception: {exc}")
        # Safe message: never expose stack trace, local filepaths, or secrets
        content = ErrorResponse(
            success=False,
            error=ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected internal server error occurred. Our team has been notified.",
                details=[],
            ),
            request_id=req_id,
        ).model_dump()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)
