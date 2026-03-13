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
                "models.invoice", "models.msp_workflow",
                "models.rate_card", "models.compliance",
                "models.sla", "models.expense",
                "models.crm", "models.ats", "models.automation",
                "models.import_job",
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
    """Seed multi-tenant demo data on every cold start (SQLite in /tmp is ephemeral)."""
    from sqlalchemy import text
    from datetime import datetime
    from utils.security import hash_password
    
    now = datetime.utcnow()
    
    async with async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)() as session:
        # Clear stale seed data
        await session.execute(text("DELETE FROM rate_cards"))
        await session.execute(text("DELETE FROM compliance_requirements"))
        await session.execute(text("DELETE FROM sla_configurations"))
        await session.execute(text("DELETE FROM organization_memberships"))
        await session.execute(text("DELETE FROM organizations"))
        await session.execute(text("DELETE FROM users WHERE id IN (1, 2, 3, 4, 5, 6, 7)"))
        
        # Create Organizations
        # 1. MSP Organization
        await session.execute(text(
            "INSERT INTO organizations (id, name, slug, org_type, onboarding_status, "
            "primary_contact_name, primary_contact_email, industry, is_active, created_at, updated_at) "
            "VALUES (:id, :name, :slug, :type, :status, :contact_name, :contact_email, :industry, 1, :now, :now)"
        ), {
            "id": 1, "name": "HotGigs MSP", "slug": "hotgigs-msp", "type": "MSP",
            "status": "ACTIVE", "contact_name": "Raj Patel", "contact_email": "admin@hotgigs.ai",
            "industry": "Staffing & Recruitment", "now": now
        })
        
        # 2. Client Organization
        await session.execute(text(
            "INSERT INTO organizations (id, name, slug, org_type, onboarding_status, "
            "primary_contact_name, primary_contact_email, industry, parent_org_id, is_active, created_at, updated_at) "
            "VALUES (:id, :name, :slug, :type, :status, :contact_name, :contact_email, :industry, :parent_id, 1, :now, :now)"
        ), {
            "id": 2, "name": "TechCorp Inc", "slug": "techcorp-inc", "type": "CLIENT",
            "status": "ACTIVE", "contact_name": "Sarah Johnson", "contact_email": "admin@techcorp.com",
            "industry": "Technology", "parent_id": 1, "now": now
        })
        
        # 3. Supplier Organization
        await session.execute(text(
            "INSERT INTO organizations (id, name, slug, org_type, onboarding_status, "
            "primary_contact_name, primary_contact_email, industry, tier, parent_org_id, is_active, created_at, updated_at) "
            "VALUES (:id, :name, :slug, :type, :status, :contact_name, :contact_email, :industry, :tier, :parent_id, 1, :now, :now)"
        ), {
            "id": 3, "name": "StaffPro Solutions", "slug": "staffpro-solutions", "type": "SUPPLIER",
            "status": "ACTIVE", "contact_name": "Michael Chen", "contact_email": "contact@staffpro.com",
            "industry": "Staffing", "tier": "GOLD", "parent_id": 1, "now": now
        })
        
        # Hash passwords
        msp_admin_pw = hash_password("Demo123456")
        msp_recruiter_pw = hash_password("Demo123456")
        client_mgr_pw = hash_password("Demo123456")
        supplier_rec_pw = hash_password("Demo123456")
        demo_user_pw = hash_password("Demo123456")
        
        # Create Users
        # 1. MSP Admin
        await session.execute(text(
            "INSERT INTO users (id, email, first_name, last_name, hashed_password, role, "
            "organization_id, is_active, created_at, updated_at) "
            "VALUES (:id, :email, :fn, :ln, :pw, :role, :org_id, 1, :now, :now)"
        ), {
            "id": 1, "email": "msp_admin@hotgigs.com", "fn": "Admin", "ln": "User",
            "pw": msp_admin_pw, "role": "MSP_ADMIN", "org_id": 1, "now": now
        })
        
        # 2. MSP Recruiter
        await session.execute(text(
            "INSERT INTO users (id, email, first_name, last_name, hashed_password, role, "
            "organization_id, is_active, created_at, updated_at) "
            "VALUES (:id, :email, :fn, :ln, :pw, :role, :org_id, 1, :now, :now)"
        ), {
            "id": 2, "email": "msp_recruiter@hotgigs.com", "fn": "Jane", "ln": "Recruiter",
            "pw": msp_recruiter_pw, "role": "MSP_RECRUITER", "org_id": 1, "now": now
        })
        
        # 3. Client Manager
        await session.execute(text(
            "INSERT INTO users (id, email, first_name, last_name, hashed_password, role, "
            "organization_id, is_active, created_at, updated_at) "
            "VALUES (:id, :email, :fn, :ln, :pw, :role, :org_id, 1, :now, :now)"
        ), {
            "id": 3, "email": "client_mgr@techcorp.com", "fn": "Sarah", "ln": "Manager",
            "pw": client_mgr_pw, "role": "CLIENT_MANAGER", "org_id": 2, "now": now
        })
        
        # 4. Supplier Recruiter
        await session.execute(text(
            "INSERT INTO users (id, email, first_name, last_name, hashed_password, role, "
            "organization_id, is_active, created_at, updated_at) "
            "VALUES (:id, :email, :fn, :ln, :pw, :role, :org_id, 1, :now, :now)"
        ), {
            "id": 4, "email": "supplier_rec@staffpro.com", "fn": "Michael", "ln": "Chen",
            "pw": supplier_rec_pw, "role": "SUPPLIER_RECRUITER", "org_id": 3, "now": now
        })
        
        # 5. Demo user (associated with MSP org)
        await session.execute(text(
            "INSERT INTO users (id, email, first_name, last_name, hashed_password, role, "
            "organization_id, is_active, created_at, updated_at) "
            "VALUES (:id, :email, :fn, :ln, :pw, :role, :org_id, 1, :now, :now)"
        ), {
            "id": 5, "email": "demo@hrplatform.com", "fn": "Demo", "ln": "User",
            "pw": demo_user_pw, "role": "RECRUITER", "org_id": 1, "now": now
        })
        
        # Create Organization Memberships
        # MSP Admin membership (primary)
        await session.execute(text(
            "INSERT INTO organization_memberships (organization_id, user_id, role, is_primary, is_active, joined_at, created_at, updated_at) "
            "VALUES (:org_id, :user_id, :role, 1, 1, :now, :now, :now)"
        ), {
            "org_id": 1, "user_id": 1, "role": "MSP_ADMIN", "now": now
        })
        
        # MSP Recruiter membership (primary)
        await session.execute(text(
            "INSERT INTO organization_memberships (organization_id, user_id, role, is_primary, is_active, joined_at, created_at, updated_at) "
            "VALUES (:org_id, :user_id, :role, 1, 1, :now, :now, :now)"
        ), {
            "org_id": 1, "user_id": 2, "role": "MSP_RECRUITER", "now": now
        })
        
        # Client Manager membership (primary)
        await session.execute(text(
            "INSERT INTO organization_memberships (organization_id, user_id, role, is_primary, is_active, joined_at, created_at, updated_at) "
            "VALUES (:org_id, :user_id, :role, 1, 1, :now, :now, :now)"
        ), {
            "org_id": 2, "user_id": 3, "role": "CLIENT_MANAGER", "now": now
        })
        
        # Supplier Recruiter membership (primary)
        await session.execute(text(
            "INSERT INTO organization_memberships (organization_id, user_id, role, is_primary, is_active, joined_at, created_at, updated_at) "
            "VALUES (:org_id, :user_id, :role, 1, 1, :now, :now, :now)"
        ), {
            "org_id": 3, "user_id": 4, "role": "SUPPLIER_RECRUITER", "now": now
        })
        
        # Demo user membership with MSP (primary)
        await session.execute(text(
            "INSERT INTO organization_memberships (organization_id, user_id, role, is_primary, is_active, joined_at, created_at, updated_at) "
            "VALUES (:org_id, :user_id, :role, 1, 1, :now, :now, :now)"
        ), {
            "org_id": 1, "user_id": 5, "role": "RECRUITER", "now": now
        })

        # ── Rate Cards (3 records) ──────────────────────────────────────────
        # 1. Software Development rate card for TechCorp
        await session.execute(text(
            "INSERT INTO rate_cards (client_org_id, job_category, location, skill_level, "
            "bill_rate_min, bill_rate_max, pay_rate_min, pay_rate_max, overtime_multiplier, "
            "weekend_multiplier, currency, effective_from, status, is_active, created_by, created_at, updated_at) "
            "VALUES (:client_org_id, :job_category, :location, :skill_level, "
            ":bill_rate_min, :bill_rate_max, :pay_rate_min, :pay_rate_max, :overtime_mult, "
            ":weekend_mult, :currency, :effective_from, :status, 1, :created_by, :now, :now)"
        ), {
            "client_org_id": 2, "job_category": "Software Development", "location": "Remote",
            "skill_level": "Senior", "bill_rate_min": 80.0, "bill_rate_max": 150.0,
            "pay_rate_min": 60.0, "pay_rate_max": 120.0, "overtime_mult": 1.5, "weekend_mult": 1.25,
            "currency": "USD", "effective_from": now.date(), "status": "ACTIVE", "created_by": 1, "now": now
        })

        # 2. Data Engineering rate card for TechCorp
        await session.execute(text(
            "INSERT INTO rate_cards (client_org_id, job_category, location, skill_level, "
            "bill_rate_min, bill_rate_max, pay_rate_min, pay_rate_max, overtime_multiplier, "
            "weekend_multiplier, currency, effective_from, status, is_active, created_by, created_at, updated_at) "
            "VALUES (:client_org_id, :job_category, :location, :skill_level, "
            ":bill_rate_min, :bill_rate_max, :pay_rate_min, :pay_rate_max, :overtime_mult, "
            ":weekend_mult, :currency, :effective_from, :status, 1, :created_by, :now, :now)"
        ), {
            "client_org_id": 2, "job_category": "Data Engineering", "location": "New York",
            "skill_level": "Senior", "bill_rate_min": 90.0, "bill_rate_max": 160.0,
            "pay_rate_min": 70.0, "pay_rate_max": 130.0, "overtime_mult": 1.5, "weekend_mult": 1.25,
            "currency": "USD", "effective_from": now.date(), "status": "ACTIVE", "created_by": 1, "now": now
        })

        # 3. QA Testing rate card (draft status)
        await session.execute(text(
            "INSERT INTO rate_cards (client_org_id, job_category, location, skill_level, "
            "bill_rate_min, bill_rate_max, pay_rate_min, pay_rate_max, overtime_multiplier, "
            "weekend_multiplier, currency, effective_from, status, is_active, created_by, created_at, updated_at) "
            "VALUES (:client_org_id, :job_category, :location, :skill_level, "
            ":bill_rate_min, :bill_rate_max, :pay_rate_min, :pay_rate_max, :overtime_mult, "
            ":weekend_mult, :currency, :effective_from, :status, 1, :created_by, :now, :now)"
        ), {
            "client_org_id": 2, "job_category": "QA Testing", "location": "Remote",
            "skill_level": "Mid-Level", "bill_rate_min": 50.0, "bill_rate_max": 90.0,
            "pay_rate_min": 35.0, "pay_rate_max": 70.0, "overtime_mult": 1.5, "weekend_mult": 1.25,
            "currency": "USD", "effective_from": now.date(), "status": "DRAFT", "created_by": 1, "now": now
        })

        # ── Compliance Requirements (4 records) ────────────────────────────
        # 1. Background check requirement (org_id=1, mandatory, risk_level=8)
        await session.execute(text(
            "INSERT INTO compliance_requirements (organization_id, requirement_type, is_mandatory, "
            "description, risk_level, is_active, created_at, updated_at) "
            "VALUES (:org_id, :req_type, 1, :description, :risk_level, 1, :now, :now)"
        ), {
            "org_id": 1, "req_type": "BACKGROUND_CHECK", "description": "Criminal background check required for all placements",
            "risk_level": "8", "now": now
        })

        # 2. Drug screening requirement (org_id=1, mandatory, risk_level=7)
        await session.execute(text(
            "INSERT INTO compliance_requirements (organization_id, requirement_type, is_mandatory, "
            "description, risk_level, is_active, created_at, updated_at) "
            "VALUES (:org_id, :req_type, 1, :description, :risk_level, 1, :now, :now)"
        ), {
            "org_id": 1, "req_type": "DRUG_TEST", "description": "Drug screening test required for all placements",
            "risk_level": "7", "now": now
        })

        # 3. NDA requirement (org_id=1, mandatory, risk_level=5)
        await session.execute(text(
            "INSERT INTO compliance_requirements (organization_id, requirement_type, is_mandatory, "
            "description, risk_level, is_active, created_at, updated_at) "
            "VALUES (:org_id, :req_type, 1, :description, :risk_level, 1, :now, :now)"
        ), {
            "org_id": 1, "req_type": "CERTIFICATION", "description": "NDA signature required before placement",
            "risk_level": "5", "now": now
        })

        # 4. Professional certification (org_id=2, not mandatory, risk_level=3)
        await session.execute(text(
            "INSERT INTO compliance_requirements (organization_id, requirement_type, is_mandatory, "
            "description, risk_level, is_active, created_at, updated_at) "
            "VALUES (:org_id, :req_type, 0, :description, :risk_level, 1, :now, :now)"
        ), {
            "org_id": 2, "req_type": "CERTIFICATION", "description": "Professional certifications relevant to job category",
            "risk_level": "3", "now": now
        })

        # ── SLA Configurations (2 records) ─────────────────────────────────
        # 1. Standard SLA for org_id=1
        await session.execute(text(
            "INSERT INTO sla_configurations (organization_id, name, response_time_hours, fill_time_days, "
            "min_quality_score, min_acceptance_rate, min_retention_days, response_time_penalty, is_active, created_at, updated_at) "
            "VALUES (:org_id, :name, :response_hours, :fill_days, :quality_score, :acceptance_rate, "
            ":retention_days, :penalty, 1, :now, :now)"
        ), {
            "org_id": 1, "name": "Standard SLA", "response_hours": 24, "fill_days": 15,
            "quality_score": 70.0, "acceptance_rate": 0.8, "retention_days": 90,
            "penalty": 500.0, "now": now
        })

        # 2. Premium SLA for org_id=2
        await session.execute(text(
            "INSERT INTO sla_configurations (organization_id, name, response_time_hours, fill_time_days, "
            "min_quality_score, min_acceptance_rate, min_retention_days, response_time_penalty, is_active, created_at, updated_at) "
            "VALUES (:org_id, :name, :response_hours, :fill_days, :quality_score, :acceptance_rate, "
            ":retention_days, :penalty, 1, :now, :now)"
        ), {
            "org_id": 2, "name": "Premium SLA", "response_hours": 8, "fill_days": 7,
            "quality_score": 85.0, "acceptance_rate": 0.9, "retention_days": 180,
            "penalty": 1000.0, "now": now
        })

        await session.commit()
    
    print("Seeded multi-tenant demo organizations and users")

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

# ── Patch passlib to use bcrypt directly (avoids detect_wrap_bug crash) ──
try:
    import bcrypt as _bcrypt_lib
    def _verify_pw(plain: str, hashed: str) -> bool:
        try:
            return _bcrypt_lib.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False
    def _hash_pw(plain: str) -> str:
        return _bcrypt_lib.hashpw(plain.encode("utf-8"), _bcrypt_lib.gensalt()).decode("utf-8")
    import utils.security as _sec
    _sec.verify_password = _verify_pw
    _sec.hash_password = _hash_pw
    _sec.pwd_context = None  # disable passlib entirely
    print("Patched password functions to use bcrypt directly")
except Exception as _pe:
    print(f"bcrypt patch failed: {_pe}")

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
        ("auth", "Auth"), ("dashboard", "Dashboard"), ("reports", "Reports & Analytics"),
        ("analytics", "Analytics"),
        ("interviews", "Interviews"), ("matching", "Matching"),
        ("offers", "Offers"), ("resumes", "Resumes"),
        ("submissions", "Submissions"), ("suppliers", "Suppliers"),
        ("job_posts", "Job Posts"), ("clients", "Clients"),
        ("contracts", "Contracts"), ("candidate_portal", "Candidates"),
        ("referrals", "Referrals"), ("negotiations", "Negotiations"),
        ("security", "Security"), ("admin", "Admin"),
        ("messaging", "Messaging"), ("payments", "Payments"),
        ("timesheets", "Timesheets"), ("invoices", "Invoices"),
        ("organizations", "Organizations"), ("msp", "MSP"),
        ("client_portal", "Client Portal"), ("supplier_portal", "Supplier Portal"),
        ("rate_cards", "Rate Cards"), ("compliance_mgmt", "Compliance"),
        ("sla", "SLA"), ("vms_timesheets", "VMS Timesheets"),
        ("auto_invoicing", "Auto Invoicing"),
        ("search", "Advanced Search"), ("automation", "Automation"),
        ("crm", "Candidate CRM"), ("ats", "ATS Enhancement"),
        ("bulk_operations", "Bulk Operations"),
        ("aggregate_reports", "Aggregate Reports"),
        ("custom_reports", "Custom Reports"),
        ("test_agent", "Testing Agent"),
        ("resume_processing", "Resume Processing"),
        ("pipeline_analytics", "Pipeline Analytics & Notifications"),
        ("msp_billing", "MSP Billing & Cascading Invoices"),
        ("bgc_onboarding", "BGC & Onboarding"),
        ("asset_management", "Asset Management"),
        ("email_agent", "Email Agent"),
        ("email_resume_processor", "Email Resume Processing"),
        ("notification_hub", "Notification Hub"),
        ("mom_action_items", "MOM & Action Items"),
        ("app_admin_config", "App Admin Configuration"),
        ("company_admin_config", "Company Admin Configuration"),
        ("financial_reports", "Financial Reports"),
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
