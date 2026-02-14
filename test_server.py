"""
Test Server - Lightweight deployment for testing without Redis/RabbitMQ/PostgreSQL.
Uses SQLite + in-memory event bus for local testing.
"""
import sys
import os
import logging
import asyncio
from datetime import datetime

# Ensure hr_platform is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set env before importing anything
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./hr_platform_test.db"
os.environ["DATABASE_SYNC_URL"] = "sqlite:///./hr_platform_test.db"
os.environ["DEBUG"] = "true"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ── Step 1: Patch the database connection for SQLite ──
def patch_database():
    """Replace PostgreSQL engine with SQLite for testing."""
    import database.connection as db_conn
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

    async def init_db_sqlite():
        """Init with SQLite instead of PostgreSQL."""
        db_conn.engine = create_async_engine(
            "sqlite+aiosqlite:///./hr_platform_test.db",
            echo=False,
            connect_args={"check_same_thread": False},
        )
        db_conn.AsyncSessionLocal = async_sessionmaker(
            db_conn.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        logger.info("SQLite database engine initialized")

    async def close_db_sqlite():
        if db_conn.engine:
            await db_conn.engine.dispose()
            logger.info("SQLite database engine closed")

    async def check_db_health_sqlite():
        if db_conn.engine is None:
            return {"status": "not_initialized", "database": "sqlite"}
        try:
            from sqlalchemy import text
            async with db_conn.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "sqlite"}
        except Exception as e:
            return {"status": "unhealthy", "database": "sqlite", "error": str(e)}

    # Monkey-patch
    db_conn.init_db = init_db_sqlite
    db_conn.close_db = close_db_sqlite
    db_conn.check_db_health = check_db_health_sqlite

    # Also patch the __init__ imports
    import database as db_mod
    db_mod.init_db = init_db_sqlite
    db_mod.close_db = close_db_sqlite
    db_mod.check_db_health = check_db_health_sqlite


# ── Step 2: Patch the event bus to use in-memory ──
def patch_event_bus():
    """Replace Redis/RabbitMQ event bus with in-memory version."""
    import agents.event_bus as eb_mod

    class InMemoryBroker(eb_mod.EventBroker):
        """Simple in-memory event broker for testing."""

        def __init__(self):
            self._subscriptions = {}
            self._dead_letter = []

        async def publish(self, event, queue=None):
            event_type = event.event_type
            if event_type in self._subscriptions:
                for cb in self._subscriptions[event_type]:
                    try:
                        await cb(event)
                    except Exception as e:
                        logger.error(f"Event handler error: {e}")
                        self._dead_letter.append(event)

        async def subscribe(self, event_type, callback):
            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []
            self._subscriptions[event_type].append(callback)

        async def unsubscribe(self, event_type, callback):
            if event_type in self._subscriptions:
                self._subscriptions[event_type] = [
                    cb for cb in self._subscriptions[event_type] if cb != callback
                ]

        async def close(self):
            self._subscriptions.clear()

    class TestEventBus:
        """Simplified event bus for testing."""

        def __init__(self):
            self.broker = InMemoryBroker()

        async def initialize(self):
            logger.info("In-memory event bus initialized")

        async def publish(self, event, queue=None):
            await self.broker.publish(event, queue)

        async def subscribe(self, event_type, callback):
            await self.broker.subscribe(event_type, callback)

        async def close(self):
            await self.broker.close()

        async def retry_dead_letter_queue(self):
            pass

    # Store for patching main app
    eb_mod._test_event_bus_class = TestEventBus


# ── Step 3: Patch the CORS validator ──
def patch_settings():
    """Ensure settings work with test values."""
    import importlib
    import sys

    # Import the actual module (not the cached settings object)
    mod = importlib.import_module("config.settings")
    mod.get_settings.cache_clear()

    from config.settings import Settings
    new_settings = Settings()

    # Update the module-level settings variable
    sys.modules["config.settings"].__dict__["settings"] = new_settings
    sys.modules["config"].__dict__["settings"] = new_settings
    logger.info(f"Settings patched: DB={new_settings.database_url}")


# ── Step 4: Create tables ──
async def create_tables():
    """Create all database tables."""
    from database.base import Base
    from database.connection import engine

    # Import all models to register them with Base.metadata
    import_models()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info(f"Created {len(Base.metadata.tables)} database tables")
    for table_name in sorted(Base.metadata.tables.keys()):
        logger.info(f"  - {table_name}")


def import_models():
    """Import all model modules to register them with SQLAlchemy."""
    model_modules = [
        "models.user",
        "models.candidate",
        "models.requirement",
        "models.submission",
        "models.interview",
        "models.offer",
        "models.supplier",
        "models.contract",
        "models.referral",
        "models.messaging",
        "models.payment",
        "models.timesheet",
        "models.invoice",
    ]

    for mod_name in model_modules:
        try:
            __import__(mod_name)
            logger.info(f"  Loaded model: {mod_name}")
        except ImportError as e:
            logger.warning(f"  Skipped model {mod_name}: {e}")
        except Exception as e:
            logger.warning(f"  Error loading {mod_name}: {e}")


# ── Step 5: Seed test data ──
async def seed_test_data():
    """Insert seed data for testing."""
    from database.connection import AsyncSessionLocal
    from sqlalchemy import text

    if AsyncSessionLocal is None:
        logger.warning("No session factory - skipping seed data")
        return

    async with AsyncSessionLocal() as session:
        # Check if data already exists
        result = await session.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"))
        table_count = result.scalar()
        logger.info(f"Database has {table_count} tables")

    logger.info("Test database ready (seed data can be added via API)")


# ── Step 6: Build the test app ──
def create_test_app():
    """Create FastAPI app configured for testing."""
    from fastapi import FastAPI, status
    from fastapi.responses import JSONResponse
    from starlette.middleware.cors import CORSMiddleware
    from config import settings

    app = FastAPI(
        title=f"{settings.app_name}",
        description="Enterprise HR Automation Platform - Test Deployment",
        version="2.0.0-test",
        debug=True,
    )

    # CORS
    origins = settings.cors_origins if isinstance(settings.cors_origins, list) else [settings.cors_origins]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware
    from api.middleware import RequestLoggingMiddleware
    app.add_middleware(RequestLoggingMiddleware)

    # Startup
    @app.on_event("startup")
    async def startup():
        from database import init_db
        await init_db()
        await create_tables()
        await seed_test_data()
        logger.info("Test server started successfully!")

    # Shutdown
    @app.on_event("shutdown")
    async def shutdown():
        from database import close_db
        await close_db()

    # Health check
    @app.get("/health")
    async def health():
        from database.connection import check_db_health
        db_health = await check_db_health()
        return {
            "status": "healthy" if db_health.get("status") == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "mode": "test",
            "checks": {"database": db_health},
        }

    @app.get("/")
    async def root():
        return {
            "message": settings.app_name,
            "version": "2.0.0-test",
            "status": "running",
            "mode": "test",
            "modules": 27,
            "agents": 32,
        }

    # Try to include v1 router
    try:
        from api.v1.router import router as v1_router
        app.include_router(v1_router)
        logger.info("V1 API router loaded with all 27 modules")
    except Exception as e:
        logger.error(f"Failed to load V1 router: {e}")
        # Create a fallback status endpoint
        @app.get("/api/v1/status")
        async def v1_status():
            return {"error": f"V1 router failed to load: {str(e)}"}

    # Global error handler
    @app.exception_handler(Exception)
    async def global_error(request, exc):
        logger.error(f"Error: {exc}", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__},
        )

    return app


def main():
    """Run the test server."""
    logger.info("=" * 60)
    logger.info("  HR Automation Platform - Test Deployment")
    logger.info("=" * 60)

    # Apply patches before importing app modules
    logger.info("Patching for test environment...")
    patch_settings()
    patch_database()
    patch_event_bus()

    # Create and run app
    app = create_test_app()

    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    main()
