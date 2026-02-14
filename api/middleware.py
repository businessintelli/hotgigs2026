import logging
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from config import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request and response details.

        Args:
            request: The HTTP request
            call_next: Next middleware/handler

        Returns:
            The HTTP response
        """
        # Add request ID to state
        request.state.request_id = str(uuid.uuid4())
        request.state.start_time = time.time()

        # Log request
        logger.info(
            f"Request {request.state.request_id}: {request.method} {request.url.path}",
            extra={
                "request_id": request.state.request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
            },
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(
                f"Request {request.state.request_id} failed with exception",
                exc_info=exc,
                extra={"request_id": request.state.request_id},
            )
            raise

        # Log response
        process_time = time.time() - request.state.start_time
        logger.info(
            f"Request {request.state.request_id} completed: {response.status_code} ({process_time:.2f}s)",
            extra={
                "request_id": request.state.request_id,
                "status_code": response.status_code,
                "process_time": process_time,
            },
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request.state.request_id

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle exceptions."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Handle exceptions in the request.

        Args:
            request: The HTTP request
            call_next: Next middleware/handler

        Returns:
            The HTTP response
        """
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(
                f"Unhandled exception in request {request.state.request_id}",
                exc_info=exc,
            )
            raise


def setup_middleware(app):
    """Setup all middlewares for the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middlewares
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
