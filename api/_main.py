import logging
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from datetime import datetime
from database import init_db, close_db, check_db_health
from config import settings
from api.middleware import setup_middleware
from schemas.common import HealthCheckResponse
from agents.event_bus import EventBus, RedisPubSubBroker, RabbitMQBroker

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Enterprise HR Automation Platform",
    version="1.0.0",
    debug=settings.debug,
)

# Global variables for app lifecycle
event_bus: EventBus = None


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    global event_bus

    logger.info(f"Starting {settings.app_name}")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize event bus
    redis_broker = RedisPubSubBroker(settings.redis_url)
    rabbitmq_broker = RabbitMQBroker(settings.rabbitmq_url, settings.rabbitmq_queue_prefix)

    event_bus = EventBus(redis_broker=redis_broker, rabbitmq_broker=rabbitmq_broker)
    await event_bus.initialize()
    logger.info("Event bus initialized")

    logger.info(f"{settings.app_name} started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    global event_bus

    logger.info(f"Shutting down {settings.app_name}")

    # Retry dead letter queue
    if event_bus:
        await event_bus.retry_dead_letter_queue()
        await event_bus.close()

    # Close database
    await close_db()

    logger.info(f"{settings.app_name} shut down successfully")


# Setup middleware
setup_middleware(app)


@app.get("/health", response_model=HealthCheckResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint.

    Returns:
        Health check status
    """
    db_health = await check_db_health()

    return HealthCheckResponse(
        status="healthy" if db_health["status"] == "healthy" else "degraded",
        timestamp=datetime.utcnow(),
        checks={
            "database": db_health,
        },
    )


@app.get("/api/v1/health")
async def v1_health_check():
    """API v1 health check endpoint.

    Returns:
        Health check status
    """
    db_health = await check_db_health()

    return {
        "status": "healthy" if db_health["status"] == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": db_health,
        },
    }


@app.get("/")
async def root():
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": settings.app_name,
        "version": "1.0.0",
        "status": "running",
    }


# API documentation
@app.get("/docs", include_in_schema=False)
async def swagger_ui():
    """Swagger UI documentation."""
    from fastapi.openapi.docs import get_swagger_ui_html

    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.app_name} - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc():
    """ReDoc documentation."""
    from fastapi.openapi.docs import get_redoc_html

    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{settings.app_name} - ReDoc",
    )


# Include v1 API router
from api.v1.router import router as v1_router
app.include_router(v1_router)


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": getattr(request.state, "request_id", None),
        },
    )
