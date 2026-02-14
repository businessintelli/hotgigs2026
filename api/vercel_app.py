"""Vercel serverless entry point for the HR Platform.

This creates a self-contained FastAPI app that mocks unavailable
infrastructure (Redis, RabbitMQ, Elasticsearch, etc.) so the API
can run in a serverless environment with just SQLite.
"""
import sys
import os
import types
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vercel_app")

# ── 1. Add project root to path ──────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── 2. Set environment defaults ──────────────────────────────────────
defaults = {
    "DATABASE_URL": "sqlite+aiosqlite:///./hr_platform.db",
    "DATABASE_SYNC_URL": "sqlite:///./hr_platform.db",
    "REDIS_URL": "mock://localhost",
    "RABBITMQ_URL": "mock://localhost",
    "DEBUG": "false",
    "ENABLE_AI_PARSING": "false",
    "ENABLE_EMAIL_NOTIFICATIONS": "false",
    "JWT_SECRET": os.environ.get("JWT_SECRET", "vercel-dev-secret-change-me"),
}
for k, v in defaults.items():
    os.environ.setdefault(k, v)

# ── 3. Mock unavailable packages ─────────────────────────────────────
# These packages aren't installed on Vercel but are imported throughout
# the codebase. We inject lightweight stubs so imports don't crash.

def _make_mock_module(name):
    """Create a mock module that returns no-op objects for any attribute."""
    mod = types.ModuleType(name)
    class _MockClass:
        def __init__(self, *a, **kw): pass
        def __call__(self, *a, **kw): return self
        def __getattr__(self, _): return _MockClass()
        def __await__(self):
            async def _noop(): return None
            return _noop().__await__()
    mod.__dict__['__getattr__'] = lambda attr: _MockClass()
    mod.__dict__['__path__'] = []
    return mod

# Packages to mock - these are infrastructure deps not needed for serverless
_packages_to_mock = [
    "redis", "redis.asyncio", "redis.exceptions",
    "aio_pika", "aio_pika.abc",
    "elasticsearch", "elasticsearch_dsl",
    "boto3", "botocore", "botocore.exceptions",
    "sendgrid", "sendgrid.helpers", "sendgrid.helpers.mail",
    "intuit_oauth", "quickbooks", "python_quickbooks",
    "weasyprint",
    "asyncpg", "asyncpg.exceptions",
]

for pkg in _packages_to_mock:
    if pkg not in sys.modules:
        sys.modules[pkg] = _make_mock_module(pkg)

logger.info("Mocked unavailable packages for serverless environment")

# ── 4. Patch settings ────────────────────────────────────────────────
import importlib
mod = importlib.import_module("config.settings")
if hasattr(mod, "get_settings") and hasattr(mod.get_settings, "cache_clear"):
    mod.get_settings.cache_clear()
from config.settings import Settings
new_settings = Settings()
sys.modules["config.settings"].__dict__["settings"] = new_settings
sys.modules["config"].__dict__["settings"] = new_settings

# ── 5. Patch database for SQLite ─────────────────────────────────────
import database.connection as db_conn
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

_db_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./hr_platform.db")

async def init_db_vercel():
    db_conn.engine = create_async_engine(
        _db_url, echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in _db_url else {},
    )
    db_conn.AsyncSessionLocal = async_sessionmaker(
        db_conn.engine, class_=AsyncSession,
        expire_on_commit=False, autoflush=False, autocommit=False,
    )

async def close_db_vercel():
    if db_conn.engine:
        await db_conn.engine.dispose()

async def check_db_health_vercel():
    if db_conn.engine is None:
        return {"status": "not_initialized", "database": "sqlite"}
    try:
        from sqlalchemy import text
        async with db_conn.engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "sqlite"}
    except Exception as e:
        return {"status": "unhealthy", "database": "sqlite", "error": str(e)}

db_conn.init_db = init_db_vercel
db_conn.close_db = close_db_vercel
db_conn.check_db_health = check_db_health_vercel

import database as db_mod
db_mod.init_db = init_db_vercel
db_mod.close_db = close_db_vercel
db_mod.check_db_health = check_db_health_vercel

# ── 6. Patch event bus ───────────────────────────────────────────────
try:
    import agents.event_bus as eb_mod

    class InMemoryBroker(eb_mod.EventBroker):
        def __init__(self): self._subs = {}; self._dlq = []
        async def publish(self, event, queue=None):
            for cb in self._subs.get(event.event_type, []):
                try: await cb(event)
                except: self._dlq.append(event)
        async def subscribe(self, event_type, callback):
            self._subs.setdefault(event_type, []).append(callback)
        async def unsubscribe(self, event_type, callback):
            if event_type in self._subs:
                self._subs[event_type] = [c for c in self._subs[event_type] if c != callback]
        async def close(self): self._subs.clear()

    eb_mod._broker = InMemoryBroker()
except Exception as e:
    logger.warning(f"Could not patch event bus: {e}")

# ── 7. Build FastAPI app ─────────────────────────────────────────────
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HotGigs 2026 - HR Automation Platform",
    description="Enterprise HR Automation Platform by Business Intelligence",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    try:
        await init_db_vercel()
        from database.base import Base
        model_modules = [
            "models.user", "models.candidate", "models.requirement",
            "models.submission", "models.interview", "models.offer",
            "models.supplier", "models.contract", "models.referral",
            "models.messaging", "models.payment", "models.timesheet",
            "models.invoice", "models.customer", "models.security",
            "models.client", "models.copilot", "models.conversation",
            "models.alerts", "models.interview_intelligence",
        ]
        for m in model_modules:
            try:
                __import__(m)
            except Exception as ex:
                logger.warning(f"Skipped model {m}: {ex}")
        async with db_conn.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Vercel startup: DB initialized, tables created")
    except Exception as e:
        logger.error(f"Vercel startup error: {e}")

@app.on_event("shutdown")
async def shutdown():
    await close_db_vercel()

@app.get("/")
async def root():
    return {
        "platform": "HotGigs 2026",
        "company": "Business Intelligence",
        "version": "2.0.0",
        "status": "running",
        "deployment": "vercel",
        "modules": 27,
        "agents": 32,
        "docs": "/docs",
    }

@app.get("/health")
async def health():
    db_health = await check_db_health_vercel()
    return {
        "status": "healthy" if db_health.get("status") == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {"database": db_health},
    }

# ── 8. Load API routes with graceful fallback ────────────────────────
loaded_routers = []
failed_routers = []

try:
    from api.v1.router import router as v1_router
    app.include_router(v1_router)
    loaded_routers.append("v1_full")
    logger.info("V1 router loaded successfully")
except Exception as e:
    logger.warning(f"Full V1 router failed: {e}. Loading individual routes...")
    failed_routers.append(("v1_full", str(e)))

    # Try loading individual routers
    route_modules = [
        ("auth", "Authentication"),
        ("dashboard", "Dashboard"),
        ("interviews", "Interviews"),
        ("matching", "Matching"),
        ("offers", "Offers"),
        ("resumes", "Resumes"),
        ("submissions", "Submissions"),
        ("suppliers", "Suppliers"),
        ("job_posts", "Job Posts"),
        ("clients", "Clients"),
        ("contracts", "Contracts"),
        ("candidates", "Candidate Portal"),
    ]

    for module_name, tag in route_modules:
        try:
            mod = importlib.import_module(f"api.v1.{module_name}")
            if hasattr(mod, "router"):
                app.include_router(mod.router, tags=[tag])
                loaded_routers.append(module_name)
        except Exception as ex:
            failed_routers.append((module_name, str(ex)))
            logger.warning(f"Skipped router {module_name}: {ex}")

@app.get("/api/v1/status")
async def api_status():
    return {
        "loaded_routers": loaded_routers,
        "failed_routers": [{"name": n, "error": e} for n, e in failed_routers],
        "total_routes": len(app.routes),
    }

@app.exception_handler(Exception)
async def error_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc), "type": type(exc).__name__})

# ── Vercel handler ───────────────────────────────────────────────────
handler = app
