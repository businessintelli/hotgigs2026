"""Vercel serverless entry point for the HR Platform."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment defaults for Vercel
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./hr_platform.db")
os.environ.setdefault("DATABASE_SYNC_URL", "sqlite:///./hr_platform.db")
os.environ.setdefault("REDIS_URL", "mock://localhost")
os.environ.setdefault("RABBITMQ_URL", "mock://localhost")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("ENABLE_AI_PARSING", "false")
os.environ.setdefault("ENABLE_EMAIL_NOTIFICATIONS", "false")

import importlib
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Patch settings
mod = importlib.import_module("config.settings")
mod.get_settings.cache_clear()
from config.settings import Settings
new_settings = Settings()
sys.modules["config.settings"].__dict__["settings"] = new_settings
sys.modules["config"].__dict__["settings"] = new_settings

# Patch database for SQLite
import database.connection as db_conn
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

async def init_db_vercel():
    db_conn.engine = create_async_engine(
        os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./hr_platform.db"),
        echo=False,
        connect_args={"check_same_thread": False},
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

# Patch event bus
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

# Build FastAPI app
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HR Automation Platform",
    description="Enterprise HR Automation Platform - Vercel Deployment",
    version="2.0.0",
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
    await init_db_vercel()
    # Create tables
    from database.base import Base
    models = ["models.user", "models.candidate", "models.requirement", "models.submission",
              "models.interview", "models.offer", "models.supplier", "models.contract",
              "models.referral", "models.messaging", "models.payment", "models.timesheet", "models.invoice"]
    for m in models:
        try: __import__(m)
        except: pass
    async with db_conn.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Vercel: DB initialized")

@app.on_event("shutdown")
async def shutdown():
    await close_db_vercel()

@app.get("/")
async def root():
    return {
        "message": "HR Automation Platform",
        "version": "2.0.0",
        "status": "running",
        "deployment": "vercel",
        "modules": 27,
        "agents": 32,
    }

@app.get("/health")
async def health():
    db_health = await check_db_health_vercel()
    return {"status": "healthy" if db_health["status"] == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(), "checks": {"database": db_health}}

# Include V1 router
try:
    from api.v1.router import router as v1_router
    app.include_router(v1_router)
    logger.info("V1 router loaded")
except Exception as e:
    logger.error(f"Failed to load V1 router: {e}")
    @app.get("/api/v1/status")
    async def v1_error():
        return {"error": str(e)}

@app.exception_handler(Exception)
async def error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc)})

# Vercel handler
handler = app
