import contextvars
import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Union

# Context variable tracking correlation/request ID across asynchronous execution contexts
correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Retrieve the current request correlation ID from task context."""
    return correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> contextvars.Token:
    """Set the correlation ID for the current task context."""
    return correlation_id_ctx.set(correlation_id)


def reset_correlation_id(token: contextvars.Token) -> None:
    """Reset the correlation ID context var to its previous state."""
    correlation_id_ctx.reset(token)


# Substrings in dictionary keys that indicate sensitive data
SENSITIVE_KEY_SUBSTRINGS: Set[str] = {
    "password",
    "passwd",
    "secret",
    "token",
    "auth",
    "api_key",
    "apikey",
    "credential",
    "credentials",
    "private_key",
    "card_number",
    "cvv",
    "ssn",
    "aadhaar",
    "otp",
}

# Standalone exact key matches (to prevent false positives like 'panel' or 'span')
SENSITIVE_EXACT_KEYS: Set[str] = {
    "pan",
    "pan_number",
    "pancard",
    "pin",
}

# Regex patterns for sanitizing sensitive data within plain text strings
BEARER_TOKEN_REGEX = re.compile(r"(Bearer\s+)[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE)
DATABASE_URL_CRED_REGEX = re.compile(r"(://[^:\s]+:)([^@\s]+)(@)")
KEY_VALUE_SECRET_REGEX = re.compile(
    r'(["\']?(?:[\w\-_]*(?:password|secret|token|auth|credential|api_key)[\w\-_]*)["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])',
    re.IGNORECASE,
)
UNQUOTED_CONN_SECRET_REGEX = re.compile(
    r'((?:password|pwd|secret)\s*=\s*)([^\s,;]+)',
    re.IGNORECASE,
)
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
AADHAAR_REGEX = re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b")


def is_sensitive_key(key: str) -> bool:
    """Check if a dictionary key represents sensitive credentials or personal data."""
    k_lower = key.lower()
    if k_lower in SENSITIVE_EXACT_KEYS:
        return True
    return any(sub in k_lower for sub in SENSITIVE_KEY_SUBSTRINGS)


def mask_sensitive_data(val: Any) -> Any:
    """
    Recursively sanitize sensitive values from dicts, lists, tuples, or strings.
    Guarantees that credentials, tokens, credit cards, SSNs and Aadhaar numbers
    are masked before logging or response serialization.
    """
    if isinstance(val, dict):
        sanitized_dict: Dict[str, Any] = {}
        for k, v in val.items():
            if is_sensitive_key(str(k)):
                sanitized_dict[k] = "[REDACTED]"
            else:
                sanitized_dict[k] = mask_sensitive_data(v)
        return sanitized_dict
    elif isinstance(val, (list, tuple, set)):
        sanitized_seq = [mask_sensitive_data(item) for item in val]
        return type(val)(sanitized_seq)
    elif isinstance(val, str):
        cleaned = BEARER_TOKEN_REGEX.sub(r"\1[REDACTED]", val)
        cleaned = DATABASE_URL_CRED_REGEX.sub(r"\1[REDACTED]\3", cleaned)
        cleaned = KEY_VALUE_SECRET_REGEX.sub(r"\1[REDACTED]\3", cleaned)
        cleaned = UNQUOTED_CONN_SECRET_REGEX.sub(r"\1[REDACTED]", cleaned)
        cleaned = CREDIT_CARD_REGEX.sub("[REDACTED_CARD]", cleaned)
        cleaned = SSN_REGEX.sub("[REDACTED_SSN]", cleaned)
        cleaned = AADHAAR_REGEX.sub("[REDACTED_AADHAAR]", cleaned)
        return cleaned
    return val


class CorrelationIdFilter(logging.Filter):
    """
    Injects request_id from contextvars into every LogRecord automatically.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        cid = get_correlation_id()
        record.request_id = cid if cid else "-"
        return True


class SensitiveDataFilter(logging.Filter):
    """
    Intercepts and sanitizes all log record messages and arguments.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = mask_sensitive_data(record.msg)
        if record.args:
            record.args = mask_sensitive_data(record.args)
        return True


class JSONLogFormatter(logging.Formatter):
    """
    Production-grade structured JSON log formatter compatible with
    observability systems (Datadog, Loki, CloudWatch, ELK).
    """
    def __init__(self, service_name: str = "university-erp", environment: str = "production"):
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        req_id = getattr(record, "request_id", None) or get_correlation_id() or "-"

        log_payload: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": req_id,
            "service": self.service_name,
            "environment": self.environment,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Formatted stack trace if exception exists
        if record.exc_info:
            raw_exc = self.formatException(record.exc_info)
            log_payload["exception"] = mask_sensitive_data(raw_exc)

        # Include custom extra fields passed to logger calls
        standard_record_fields = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "request_id", "message"
        }
        extras: Dict[str, Any] = {}
        for k, v in record.__dict__.items():
            if k not in standard_record_fields and not k.startswith("_"):
                if is_sensitive_key(k):
                    extras[k] = "[REDACTED]"
                else:
                    extras[k] = mask_sensitive_data(v)
        if extras:
            log_payload["extra"] = extras

        return json.dumps(log_payload, default=str)


class ConsoleLogFormatter(logging.Formatter):
    """
    Human-readable log formatter for local development with correlation IDs and timestamps.
    """
    def format(self, record: logging.LogRecord) -> str:
        req_id = getattr(record, "request_id", None) or get_correlation_id() or "-"
        req_tag = f"[{req_id}] " if req_id != "-" else ""
        date_str = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        msg = record.getMessage()

        line = f"{date_str} | {record.levelname:<8} | {req_tag}{record.name}:{record.funcName}:{record.lineno} - {msg}"
        if record.exc_info:
            line += "\n" + mask_sensitive_data(self.formatException(record.exc_info))
        return line


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    environment: Optional[str] = None,
) -> None:
    """
    Configure application-wide logging based on environment and settings.
    Supports structured JSON (production/staging) and readable text (development).
    """
    from app.core.config import settings

    effective_level_str = (log_level or getattr(settings, "LOG_LEVEL", "INFO")).upper()
    level_num = getattr(logging, effective_level_str, logging.INFO)

    effective_env = environment or getattr(settings, "ENVIRONMENT", "development")
    effective_format = (log_format or getattr(settings, "LOG_FORMAT", "text")).lower()

    if effective_format == "auto":
        effective_format = "json" if effective_env in ("production", "staging") else "text"

    # Instantiate chosen formatter
    if effective_format == "json":
        formatter = JSONLogFormatter(service_name="university-erp", environment=effective_env)
    else:
        formatter = ConsoleLogFormatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(CorrelationIdFilter())
    handler.addFilter(SensitiveDataFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level_num)
    root_logger.handlers = [handler]

    # Application logger configuration
    app_logger = logging.getLogger("university_erp")
    app_logger.setLevel(level_num)
    app_logger.propagate = True

    # Suppress verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


# Default application-wide logger
logger = logging.getLogger("university_erp")
