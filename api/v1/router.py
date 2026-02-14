"""Main v1 router that aggregates all sub-routers."""

import logging
from fastapi import APIRouter

# Import all v1 routers
from api.v1 import (
    auth,
    dashboard,
    interviews,
    matching,
    offers,
    resumes,
    submissions,
    suppliers,
    copilot,
    rediscovery,
    job_posts,
    harvest,
    marketing,
    alerts,
    contracts,
    candidate_portal,
    referrals,
    negotiations,
    conversations,
    security,
    admin,
    cicd,
    clients,
    messaging,
    payments,
    timesheets,
    invoices,
)

logger = logging.getLogger(__name__)

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# ── Core Modules ──
router.include_router(auth.router, tags=["Authentication"])
router.include_router(dashboard.router, tags=["Dashboard & Analytics"])

# ── Requirement & Candidate Pipeline ──
router.include_router(resumes.router, tags=["Resumes & Parsing"])
router.include_router(matching.router, tags=["Matching Engine"])
router.include_router(interviews.router, tags=["Interviews"])
router.include_router(submissions.router, tags=["Submissions"])
router.include_router(offers.router, tags=["Offers & Onboarding"])
router.include_router(negotiations.router, tags=["Rate Negotiation & Scheduling"])

# ── AI-Powered Agents ──
router.include_router(copilot.router, tags=["AI Recruiter Copilot"])
router.include_router(conversations.router, tags=["Conversational AI Interface"])
router.include_router(rediscovery.router, tags=["Candidate Rediscovery"])
router.include_router(job_posts.router, tags=["Job Post Intelligence"])

# ── Sourcing & Marketing ──
router.include_router(harvest.router, tags=["Resume Harvesting"])
router.include_router(marketing.router, tags=["Digital Marketing"])

# ── Candidate Self-Service ──
router.include_router(candidate_portal.router, tags=["Candidate Portal"])

# ── Contracts & E-Signatures ──
router.include_router(contracts.router, tags=["Contract Management"])

# ── Network Management ──
router.include_router(suppliers.router, tags=["Supplier Network"])
router.include_router(referrals.router, tags=["Referral Network"])
router.include_router(clients.router, tags=["Client Management"])

# ── Messaging & Communications ──
router.include_router(messaging.router, tags=["Slack & Teams Integration"])

# ── Financial Operations ──
router.include_router(payments.router, tags=["Payment Processing"])
router.include_router(timesheets.router, tags=["Timesheet Tracking"])
router.include_router(invoices.router, tags=["Invoicing & QuickBooks"])

# ── Platform Administration ──
router.include_router(alerts.router, tags=["Alerts & Notifications"])
router.include_router(security.router, tags=["Security & RBAC"])
router.include_router(admin.router, tags=["Administration"])
router.include_router(cicd.router, tags=["CI/CD & Deployment"])


@router.get("", tags=["Status"])
async def v1_status():
    """Get v1 API status with module inventory."""
    return {
        "status": "ready",
        "version": "2.0.0",
        "platform": "HR Automation Platform",
        "modules": {
            "core": ["auth", "dashboard"],
            "pipeline": ["resumes", "matching", "interviews", "submissions", "offers", "negotiations"],
            "ai_agents": ["copilot", "conversations", "rediscovery", "job_posts"],
            "sourcing": ["harvest", "marketing"],
            "self_service": ["candidate_portal"],
            "contracts": ["contracts"],
            "network": ["suppliers", "referrals", "clients"],
            "messaging": ["messaging"],
            "financial": ["payments", "timesheets", "invoices"],
            "admin": ["alerts", "security", "admin", "cicd"],
        },
        "total_agents": 32,
        "total_api_modules": 27,
    }


logger.info("V1 router initialized with all 27 sub-routers")
