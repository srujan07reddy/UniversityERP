import json
import logging
import uuid
import httpx
import pytest
from app.core.config import Settings
from app.core.logging import (
    ConsoleLogFormatter,
    CorrelationIdFilter,
    JSONLogFormatter,
    SensitiveDataFilter,
    get_correlation_id,
    mask_sensitive_data,
    reset_correlation_id,
    set_correlation_id,
    setup_logging,
)
from app.main import app


# ==============================================================================
# Unit Tests: Correlation ID Lifecycle
# ==============================================================================

def test_correlation_id_context_lifecycle():
    """Verify context variable set, get, and reset lifecycle."""
    # Initially unset / default
    assert get_correlation_id() == ""

    test_id = str(uuid.uuid4())
    token = set_correlation_id(test_id)
    assert get_correlation_id() == test_id

    reset_correlation_id(token)
    assert get_correlation_id() == ""


# ==============================================================================
# Unit Tests: Sensitive Data Redaction / Masking
# ==============================================================================

def test_mask_sensitive_data_dictionary():
    """Verify dictionary keys matching sensitive keywords have values redacted."""
    sensitive_payload = {
        "username": "student_john",
        "email": "john@jeppiaar.ac.in",
        "password": "superSecretPassword123",
        "nested": {
            "access_token": "eyJhbGciOi...",
            "refresh_token": "dGhpc2lzYXJlZnJlc2h0b2tlbg==",
            "api_key": "erp_live_key_998877",
            "safe_counter": 42,
        },
        "student_list": [
            {"name": "Alice", "pin": "1234"},
            {"name": "Bob", "secret_note": "Confidential"},
        ],
    }

    sanitized = mask_sensitive_data(sensitive_payload)

    # Preserved public fields
    assert sanitized["username"] == "student_john"
    assert sanitized["email"] == "john@jeppiaar.ac.in"
    assert sanitized["nested"]["safe_counter"] == 42
    assert sanitized["student_list"][0]["name"] == "Alice"

    # Redacted fields
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["nested"]["access_token"] == "[REDACTED]"
    assert sanitized["nested"]["refresh_token"] == "[REDACTED]"
    assert sanitized["nested"]["api_key"] == "[REDACTED]"
    assert sanitized["student_list"][0]["pin"] == "[REDACTED]"
    assert sanitized["student_list"][1]["secret_note"] == "[REDACTED]"


def test_mask_sensitive_data_bearer_token():
    """Verify Bearer authorization tokens are redacted from string messages."""
    raw_str = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz.secret"
    sanitized = mask_sensitive_data(raw_str)
    assert "Bearer [REDACTED]" in sanitized
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in sanitized


def test_mask_sensitive_data_database_url():
    """Verify database connection URLs have embedded passwords redacted."""
    db_url = "postgresql+asyncpg://erp_admin:very_secret_pwd_456@db.jeppiaar.ac.in:5432/erp_prod"
    sanitized = mask_sensitive_data(db_url)
    assert "very_secret_pwd_456" not in sanitized
    assert "postgresql+asyncpg://erp_admin:[REDACTED]@db.jeppiaar.ac.in:5432/erp_prod" in sanitized


def test_mask_sensitive_data_financial_and_pii():
    """Verify credit card numbers, SSNs, and Aadhaar numbers are redacted."""
    text_with_card = "Processed tuition payment with card 4111-2222-3333-4444 on gateway"
    text_with_ssn = "Tax identifier SSN 123-45-6789 provided for verification"
    text_with_aadhaar = "Student Aadhaar card 5555 6666 7777 presented at admissions"

    assert mask_sensitive_data(text_with_card) == "Processed tuition payment with card [REDACTED_CARD] on gateway"
    assert mask_sensitive_data(text_with_ssn) == "Tax identifier SSN [REDACTED_SSN] provided for verification"
    assert mask_sensitive_data(text_with_aadhaar) == "Student Aadhaar card [REDACTED_AADHAAR] presented at admissions"


# ==============================================================================
# Unit Tests: Log Filters & Formatters
# ==============================================================================

def test_correlation_id_filter():
    """Verify CorrelationIdFilter injects request_id from contextvar into LogRecord."""
    log_filter = CorrelationIdFilter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test event",
        args=(),
        exc_info=None,
    )

    # Without active correlation context
    log_filter.filter(record)
    assert getattr(record, "request_id", None) == "-"

    # With active correlation context
    token = set_correlation_id("test-corr-id-12345")
    try:
        log_filter.filter(record)
        assert getattr(record, "request_id", None) == "test-corr-id-12345"
    finally:
        reset_correlation_id(token)


def test_sensitive_data_filter():
    """Verify SensitiveDataFilter intercepts and redacts messages and tuple args."""
    filter_instance = SensitiveDataFilter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=20,
        msg="User authenticated with Bearer eyJhbGciOiJWTSecretToken",
        args=({"password": "rawPasswordVal", "safe": "ok"},),
        exc_info=None,
    )

    filter_instance.filter(record)

    assert "Bearer [REDACTED]" in record.msg
    assert "JWTSecretToken" not in record.msg
    args_dict = record.args if isinstance(record.args, dict) else record.args[0]
    assert args_dict["password"] == "[REDACTED]"
    assert args_dict["safe"] == "ok"


def test_json_log_formatter():
    """Verify JSONLogFormatter generates valid structured JSON with all operational fields."""
    formatter = JSONLogFormatter(service_name="test-erp", environment="production")
    record = logging.LogRecord(
        name="university_erp",
        level=logging.INFO,
        pathname="app/services/auth.py",
        lineno=42,
        msg="Student enrolled successfully",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-abc-999"
    # Custom extra attribute
    record.department_code = "CSE"
    record.secret_auth_code = "leaked-secret"

    output = formatter.format(record)
    parsed = json.loads(output)

    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "university_erp"
    assert parsed["message"] == "Student enrolled successfully"
    assert parsed["request_id"] == "req-abc-999"
    assert parsed["service"] == "test-erp"
    assert parsed["environment"] == "production"
    assert parsed["line"] == 42
    assert "timestamp" in parsed

    # Extra fields with automatic redaction
    assert "extra" in parsed
    assert parsed["extra"]["department_code"] == "CSE"
    assert parsed["extra"]["secret_auth_code"] == "[REDACTED]"


def test_console_log_formatter():
    """Verify ConsoleLogFormatter outputs readable formatted strings with request IDs."""
    formatter = ConsoleLogFormatter()
    record = logging.LogRecord(
        name="university_erp",
        level=logging.WARNING,
        pathname="app/api/v1/health.py",
        lineno=25,
        msg="Cache server slow response",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-console-001"

    output = formatter.format(record)
    assert "WARNING" in output
    assert "[req-console-001]" in output
    assert "Cache server slow response" in output


def test_environment_dependent_setup_logging():
    """Verify setup_logging properly configures root handlers according to settings."""
    # Test JSON mode configuration
    setup_logging(log_level="DEBUG", log_format="json", environment="production")
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0].formatter, JSONLogFormatter)

    # Test Text mode configuration
    setup_logging(log_level="INFO", log_format="text", environment="development")
    assert root_logger.level == logging.INFO
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0].formatter, ConsoleLogFormatter)


# ==============================================================================
# Integration Tests: Middleware Tracing & HTTP Access Logging
# ==============================================================================

@pytest.mark.asyncio
async def test_request_logging_middleware_tracing_headers():
    """Verify middleware assigns and returns X-Request-ID and X-Process-Time."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        assert "x-process-time" in response.headers
        assert response.headers["x-process-time"].endswith("ms")


@pytest.mark.asyncio
async def test_custom_request_id_preserved_and_propagated():
    """Verify client-supplied X-Request-ID header is propagated identically."""
    custom_id = f"client-corr-{uuid.uuid4()}"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/system/info",
            headers={"X-Request-ID": custom_id},
        )
        assert response.status_code == 200
        assert response.headers["x-request-id"] == custom_id
        
        # Verify body envelope matches header
        body = response.json()
        assert body["request_id"] == custom_id


@pytest.mark.asyncio
async def test_generated_request_id_matches_envelope_without_client_header():
    """Verify generated request ID in response header matches JSON body request_id."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/system/info")
        assert response.status_code == 200
        
        header_req_id = response.headers["x-request-id"]
        body_req_id = response.json()["request_id"]
        assert header_req_id == body_req_id
        assert len(header_req_id) > 10
