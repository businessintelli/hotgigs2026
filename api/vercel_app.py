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
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:////tmp/hotgigs.db")
os.environ.setdefault("DATABASE_SYNC_URL", "sqlite:////tmp/hotgigs.db")
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
            "sqlite+aiosqlite:////tmp/hotgigs.db",
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
        # Auto-seed test users
        try:
            await _seed_test_users(_engine)
        except Exception as e:
            print(f"Seeding: {e}")
    return _engine

async def _seed_test_users(engine):
    """Seed demo users on every cold start (SQLite in /tmp is ephemeral)."""
    from sqlalchemy import text
    from datetime import datetime
    now = datetime.utcnow()
    # Pre-computed bcrypt hashes (avoids passlib bug with newer bcrypt on Vercel)
    users = [
        (1, "admin@hotgigs.ai", "Platform", "Admin", "$2b$12$oHxef0tI7e9ZfKU7TODviOcD5hW1Zq8VSJsUfPyJYwuR1k4bAFU5u", "ADMIN"),
        (2, "recruiter@hotgigs.ai", "Jane", "Recruiter", "$2b$12$vVXX452oQ4k0LraVLGZZ8e.F60syRIXa1XQgOA/f3CrN1iRMWSyq.", "RECRUITER"),
        (3, "demo@hrplatform.com", "Demo", "User", "$2b$12$fjoS6UCzy9y4y.CFEUghne9LfNaRF2jU7ERAqEl0rlouiVJOOJEku", "RECRUITER"),
    ]
    async with async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)() as session:
        # Clear any stale seed data (e.g. from previous deploys with wrong role case)
        await session.execute(text("DELETE FROM users WHERE id IN (1, 2, 3)"))
        for uid, email, fn, ln, pw, role in users:
            await session.execute(text(
                "INSERT OR IGNORE INTO users (id, email, first_name, last_name, hashed_password, role, is_active, created_at, updated_at) "
                "VALUES (:id, :email, :fn, :ln, :pw, :role, 1, :now, :now)"
            ), {"id": uid, "email": email, "fn": fn, "ln": ln, "pw": pw, "role": role, "now": now})
        # Sample customers
        for cid, name, ind in [(1, "TechCorp Solutions", "Technology"), (2, "FinanceHub Global", "Finance"), (3, "HealthFirst Inc", "Healthcare")]:
            await session.execute(text(
                "INSERT OR IGNORE INTO customers (id, name, industry, is_active, created_at, updated_at) "
                "VALUES (:id, :name, :ind, 1, :now, :now)"
            ), {"id": cid, "name": name, "ind": ind, "now": now})
        await session.commit()
    print("Seeded test users and customers")

# ── Ensure DB is initialized on EVERY request ────────────────────────
# Override get_db dependency so it always inits DB first
from typing import AsyncGenerator
async def _vercel_get_db() -> AsyncGenerator[AsyncSession, None]:
    """get_db replacement that ensures engine is initialised on Vercel."""
    await _get_engine()                       # idempotent
    async with _session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

# Patch both the module-level function AND the FastAPI dependency
try:
    import database.connection as _dbc
    _orig_get_db = _dbc.get_db          # save original for dependency_overrides
    _dbc.get_db = _vercel_get_db
    import database as _dbm
    _dbm.get_db = _vercel_get_db
    # CRITICAL: also patch the already-imported reference in api.dependencies
    try:
        import api.dependencies as _adeps
        _adeps.get_db = _vercel_get_db
    except Exception:
        pass
    # Use FastAPI dependency_overrides as belt-and-suspenders
    app.dependency_overrides[_orig_get_db] = _vercel_get_db
except Exception:
    pass

# Also init on startup (if Vercel calls it)
@app.on_event("startup")
async def _startup():
    await _get_engine()

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

# ── Debug endpoint to diagnose login issues ──────────────────────────
@app.post("/api/v1/debug/login")
@app.get("/api/v1/debug/login")
async def debug_login():
    """Diagnostic endpoint that tests the full login flow step by step."""
    import traceback
    steps = {}

    # Step 1: Engine init
    try:
        engine = await _get_engine()
        steps["1_engine"] = "OK"
    except Exception as e:
        steps["1_engine"] = f"FAIL: {e}"
        return {"steps": steps, "traceback": traceback.format_exc()}

    # Step 1b: Check tables exist
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            tables = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            steps["1b_tables"] = [r[0] for r in tables]
    except Exception as e:
        steps["1b_tables"] = f"FAIL: {e}"

    # Step 2: Check users table
    try:
        async with engine.begin() as conn:
            rows = await conn.execute(text("SELECT id, email, role, is_active FROM users"))
            users = [dict(r._mapping) for r in rows]
        steps["2_users_in_db"] = users
    except Exception as e:
        steps["2_users_in_db"] = f"FAIL: {e}"
        steps["2_traceback"] = traceback.format_exc()

    # Step 2b: Force seed if empty
    if not users if isinstance(steps.get("2_users_in_db"), list) else True:
        try:
            await _seed_test_users(engine)
            steps["2b_seed"] = "SEEDED"
            # Re-check
            async with engine.begin() as conn:
                rows = await conn.execute(text("SELECT id, email, role, is_active FROM users"))
                users = [dict(r._mapping) for r in rows]
            steps["2c_users_after_seed"] = users
        except Exception as e:
            steps["2b_seed"] = f"FAIL: {e}"
            steps["2b_traceback"] = traceback.format_exc()

    # Step 3: Load user via ORM
    try:
        from models.user import User
        from sqlalchemy import select
        async with _session_factory() as session:
            stmt = select(User).where(User.email == "admin@hotgigs.ai")
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
        if user:
            steps["3_orm_user"] = {"id": user.id, "email": user.email, "role": str(user.role), "role_type": type(user.role).__name__}
        else:
            steps["3_orm_user"] = "NOT FOUND"
    except Exception as e:
        steps["3_orm_user"] = f"FAIL: {e}"
        steps["3_traceback"] = traceback.format_exc()

    # Step 4: Verify password
    try:
        from utils.security import verify_password
        if user:
            ok = verify_password("admin123456", user.hashed_password)
            steps["4_password_verify"] = "OK" if ok else "MISMATCH"
        else:
            steps["4_password_verify"] = "SKIPPED (no user)"
    except Exception as e:
        steps["4_password_verify"] = f"FAIL: {e}"
        steps["4_traceback"] = traceback.format_exc()

    # Step 5: Generate token
    try:
        from utils.security import create_access_token
        token = create_access_token(subject="1", additional_claims={"email": "admin@hotgigs.ai", "role": "admin"})
        steps["5_token"] = f"OK (len={len(token)})"
    except Exception as e:
        steps["5_token"] = f"FAIL: {e}"
        steps["5_traceback"] = traceback.format_exc()

    # Step 6: Test get_db dependency
    try:
        from database import get_db as db_get_db
        steps["6_get_db_func"] = f"{db_get_db.__module__}.{db_get_db.__name__}" if hasattr(db_get_db, '__name__') else str(db_get_db)
    except Exception as e:
        steps["6_get_db_func"] = f"FAIL: {e}"

    # Step 7: Check dependency_overrides
    steps["7_dep_overrides"] = {str(k): str(v) for k, v in app.dependency_overrides.items()}

    # Step 8: Check UserResponse.from_orm
    try:
        from schemas.auth import UserResponse
        if user:
            ur = UserResponse.model_validate(user, from_attributes=True)
            steps["8_user_response"] = {"id": ur.id, "email": ur.email, "role": ur.role}
        else:
            steps["8_user_response"] = "SKIPPED (no user)"
    except Exception as e:
        steps["8_user_response"] = f"FAIL: {e}"
        steps["8_traceback"] = traceback.format_exc()

    return {"steps": steps}

@app.get("/api/v1/status")
async def api_status():
    return {
        "loaded": _loaded,
        "failed": [{"name": n, "error": e} for n, e in _failed],
        "total_routes": len(app.routes),
    }
