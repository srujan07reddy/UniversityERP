import time
import uuid
from typing import Any, Callable
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import (
    get_correlation_id,
    logger,
    mask_sensitive_data,
    reset_correlation_id,
    set_correlation_id,
)


class RequestLoggingMiddleware:
    """
    High-performance ASGI middleware providing:
    1. Distributed Tracing & Correlation:
       - Extracts incoming 'X-Request-ID' header or creates a fresh UUID4.
       - Stores correlation ID in contextvars for downstream services and loggers.
       - Appends 'X-Request-ID' to all outgoing HTTP responses.
    2. Request Latency Measurement:
       - Calculates total request processing latency and injects 'X-Process-Time'.
    3. Structured Access Logging:
       - Logs incoming requests with method, path (query params sanitized), and client IP.
       - Logs response completions with HTTP status codes and execution times.
    4. Task Isolation:
       - Guarantees context variable teardown via contextvars.reset() on completion.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract X-Request-ID from ASGI headers or generate a new UUID
        request_id = None
        for key, val in scope.get("headers", []):
            if key.lower() == b"x-request-id":
                request_id = val.decode("latin1")
                break

        if not request_id:
            request_id = str(uuid.uuid4())

        token = set_correlation_id(request_id)
        start_time = time.perf_counter()

        method = scope.get("method", "GET")
        path = scope.get("path", "/")
        query_string = scope.get("query_string", b"").decode("latin1")
        full_path = f"{path}?{query_string}" if query_string else path
        safe_path = mask_sensitive_data(full_path)

        client = scope.get("client")
        client_ip = client[0] if client else "unknown"

        logger.info(f"--> {method} {safe_path} [client: {client_ip}]")

        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
                process_time_ms = (time.perf_counter() - start_time) * 1000

                # Clean existing duplicate tracing headers and append authoritative ones
                headers_list = [
                    (k, v)
                    for k, v in message.get("headers", [])
                    if k.lower() not in (b"x-request-id", b"x-process-time")
                ]
                headers_list.append((b"x-request-id", request_id.encode("latin1")))
                headers_list.append((b"x-process-time", f"{process_time_ms:.2f}ms".encode("latin1")))
                message["headers"] = headers_list

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"<-- {method} {safe_path} 500 in {duration_ms:.2f}ms (unhandled exception: {exc.__class__.__name__})"
            )
            raise
        else:
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_line = f"<-- {method} {safe_path} {status_code} in {duration_ms:.2f}ms"
            if status_code >= 500:
                logger.error(log_line)
            elif status_code >= 400:
                logger.warning(log_line)
            else:
                logger.info(log_line)
        finally:
            reset_correlation_id(token)


# Backwards compatibility alias
RequestTimingMiddleware = RequestLoggingMiddleware
