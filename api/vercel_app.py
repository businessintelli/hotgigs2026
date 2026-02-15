"""Vercel serverless entry point - HotGigs 2026.

Minimal standalone FastAPI app for Vercel deployment.
For full 27-module deployment, use Docker.
"""
import sys
import os

# Add project root to path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Mock ALL heavy packages before any imports ────────────────────────
import types

class _Mock:
    def __init__(self, *a, **kw): pass
    def __call__(self, *a, **kw): return _Mock()
    def __getattr__(self, n):
        if n.startswith('_'):
            raise AttributeError(n)
        return _Mock()
    def __bool__(self): return False
    def __iter__(self): return iter([])
    def __await__(self):
        async def _n(): return None
        return _n().__await__()

def _mock(name):
    m = types.ModuleType(name)
    m.__path__ = []
    m.__package__ = name
    m.__getattr__ = lambda a: _Mock
    sys.modules[name] = m

for p in [
    "redis", "redis.asyncio", "redis.exceptions",
    "aio_pika", "aio_pika.abc",
    "elasticsearch", "elasticsearch_dsl",
    "boto3", "botocore", "botocore.exceptions",
    "sendgrid", "sendgrid.helpers", "sendgrid.helpers.mail",
    "intuit_oauth", "quickbooks", "python_quickbooks",
    "weasyprint", "asyncpg", "asyncpg.exceptions", "spacy",
]:
    if p not in sys.modules:
        _mock(p)

# ── Environment ───────────────────────────────────────────────────────
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///tmp/hotgigs.db")
os.environ.setdefault("DATABASE_SYNC_URL", "sqlite:///tmp/hotgigs.db")
os.environ.setdefault("REDIS_URL", "mock://localhost")
os.environ.setdefault("RABBITMQ_URL", "mock://localhost")
os.environ.setdefault("JWT_SECRET", "vercel-dev-secret")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("ENABLE_AI_PARSING", "false")
os.environ.setdefault("ENABLE_EMAIL_NOTIFICATIONS", "false")

# ── FastAPI App ───────────────────────────────────────────────────────
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# ── Database Setup ────────────────────────────────────────────────────
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

_engine = None
_session_factory = None

async def _get_engine():
    global _engine, _session_factory
    if _engine is None:
        _engine = create_async_engine(
            "sqlite+aiosqlite:///tmp/hotgigs.db",
            echo=False,
            connect_args={"check_same_thread": False},
        )
        _session_factory = async_sessionmaker(
            _engine, class_=AsyncSession,
            expire_on_commit=False,
        )
        # Patch database module so app code can find it
        try:
            import database.connection as db_conn
            db_conn.engine = _engine
            db_conn.AsyncSessionLocal = _session_factory
        except:
            pass
        # Create tables
        try:
            from database.base import Base
            for m in [
                "models.user", "models.candidate", "models.requirement",
                "models.submission", "models.interview", "models.offer",
                "models.supplier", "models.contract", "models.referral",
                "models.customer", "models.security", "models.client",
                "models.messaging", "models.payment", "models.timesheet",
                "models.invoice",
            ]:
                try: __import__(m)
                except: pass
            async with _engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"Table creation: {e}")
    return _engine

# ── Core Routes ───────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "platform": "HotGigs 2026",
        "company": "Business Intelligence",
        "version": "2.0.0",
        "status": "running",
        "deployment": "vercel-serverless",
        "architecture": {
            "agents": 32,
            "api_modules": 27,
            "endpoints": "341+",
            "db_tables": 94,
        },
        "links": {
            "docs": "/docs",
            "health": "/health",
            "api_status": "/api/v1/status",
        },
        "note": "Full API available via Docker deployment. Vercel runs core routes.",
    }

@app.get("/health")
async def health():
    engine = await _get_engine()
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {e}"
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
    }

# ── Load V1 API Routes ───────────────────────────────────────────────
_loaded = []
_failed = []

# Patch event bus before loading routes
try:
    import agents.event_bus as eb
    class _Broker(eb.EventBroker):
        def __init__(self): self._s = {}
        async def publish(self, e, queue=None): pass
        async def subscribe(self, t, cb): self._s.setdefault(t, []).append(cb)
        async def unsubscribe(self, t, cb): pass
        async def close(self): pass
    eb._broker = _Broker()
except:
    pass

# Patch db functions
try:
    import database.connection as dbc
    async def _init(): await _get_engine()
    async def _close(): pass
    async def _health(): return {"status": "healthy"}
    dbc.init_db = _init
    dbc.close_db = _close
    dbc.check_db_health = _health
    import database as dbm
    dbm.init_db = _init
    dbm.close_db = _close
    dbm.check_db_health = _health
except:
    pass

# Patch settings
try:
    import importlib
    sm = importlib.import_module("config.settings")
    if hasattr(sm, "get_settings") and hasattr(sm.get_settings, "cache_clear"):
        sm.get_settings.cache_clear()
    from config.settings import Settings
    ns = Settings()
    sys.modules["config.settings"].__dict__["settings"] = ns
    sys.modules["config"].__dict__["settings"] = ns
except:
    pass

# Try loading the full router
try:
    from api.v1.router import router as v1_router
    app.include_router(v1_router)
    _loaded.append("v1_full")
except Exception as e:
    _failed.append(("v1_full", str(e)))
    # Fallback: load individual routers
    import importlib
    for name, tag in [
        ("auth", "Auth"), ("dashboard", "Dashboard"),
        ("interviews", "Interviews"), ("matching", "Matching"),
        ("offers", "Offers"), ("resumes", "Resumes"),
        ("submissions", "Submissions"), ("suppliers", "Suppliers"),
        ("job_posts", "Job Posts"), ("clients", "Clients"),
        ("contracts", "Contracts"), ("candidate_portal", "Candidates"),
        ("referrals", "Referrals"), ("negotiations", "Negotiations"),
        ("security", "Security"), ("admin", "Admin"),
        ("messaging", "Messaging"), ("payments", "Payments"),
        ("timesheets", "Timesheets"), ("invoices", "Invoices"),
    ]:
        try:
            mod = importlib.import_module(f"api.v1.{name}")
            if hasattr(mod, "router"):
                app.include_router(mod.router, tags=[tag])
                _loaded.append(name)
        except Exception as ex:
            _failed.append((name, str(ex)))

@app.get("/api/v1/status")
async def api_status():
    return {
        "loaded": _loaded,
        "failed": [{"name": n, "error": e} for n, e in _failed],
        "total_routes": len(app.routes),
    }
