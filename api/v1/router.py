"""Main v1 router that aggregates all sub-routers."""

import logging
from fastapi import APIRouter

# Import all v1 routers
from api.v1 import (
    auth,
    dashboard,
    reports,
    analytics,
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
    organizations,
    msp,
    client_portal,
    supplier_portal,
    rate_cards,
    compliance_mgmt,
    sla,
    vms_timesheets,
    auto_invoicing,
    crm,
    ats,
    search,
    automation,
    bulk_operations,
    aggregate_reports,
    custom_reports,
    test_agent,
    resume_processing,
    pipeline_analytics,
    msp_billing,
    bgc_onboarding,
    asset_management,
    email_agent,
    email_resume_processor,
    notification_hub,
    mom_action_items,
    app_admin_config,
    company_admin_config,
    financial_reports,
    agreements,
)

logger = logging.getLogger(__name__)

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# ── Core Modules ──
router.include_router(auth.router, tags=["Authentication"])
router.include_router(dashboard.router, tags=["Dashboard & Analytics"])
router.include_router(reports.router, tags=["Reports & Analytics"])
router.include_router(analytics.router, tags=["Advanced Analytics"])

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

# ── Multi-Tenant VMS/MSP ──
router.include_router(organizations.router, tags=["Organizations & Tenancy"])
router.include_router(msp.router, tags=["MSP Portal"])
router.include_router(client_portal.router, tags=["Client Portal"])
router.include_router(supplier_portal.router, tags=["Supplier Portal"])

# ── VMS Enhancement (Batch D) ──
router.include_router(rate_cards.router, tags=["Rate Cards"])
router.include_router(compliance_mgmt.router, tags=["Compliance Management"])
router.include_router(sla.router, tags=["SLA Management"])
router.include_router(vms_timesheets.router, tags=["VMS Timesheets"])
router.include_router(auto_invoicing.router, tags=["Auto Invoicing"])

# ── Phase 2 & 3: Candidate CRM & Enhanced ATS ──
router.include_router(crm.router, tags=["Candidate CRM"])
router.include_router(ats.router, tags=["ATS Enhancement"])

# ── Phase 4: Advanced Search, Automation & Notifications ──
router.include_router(search.router, tags=["Advanced Search"])
router.include_router(automation.router, tags=["Automation & Notifications"])

# ── Bulk Operations: Import, Export, Batch AI Analysis ──
router.include_router(bulk_operations.router, tags=["Bulk Operations"])

# ── Aggregate Reports: Cross-Dimensional Performance Analytics ──
router.include_router(aggregate_reports.router, tags=["Aggregate Reports"])

# ── Custom Report Builder & Scheduler ──
router.include_router(custom_reports.router, tags=["Custom Reports"])

# ── E2E Testing Agent ──
router.include_router(test_agent.router)

# ── Resume Processing (thumbnails, PDF conversion, tracking, condensation) ──
router.include_router(resume_processing.router, tags=["Resume Processing"])

# ── Pipeline Analytics, Email Notifications, Interview Feedback ──
router.include_router(pipeline_analytics.router, tags=["Pipeline Analytics & Notifications"])

# ── MSP Tiered Billing & Cascading Invoicing ──
router.include_router(msp_billing.router, tags=["MSP Billing & Cascading Invoices"])

# ── Background Check (BGC) & Onboarding Workflows ──
router.include_router(bgc_onboarding.router, tags=["BGC & Onboarding"])

# ── Asset Allocation & Management ──
router.include_router(asset_management.router, tags=["Asset Management"])

# ── Email Agent & Intelligence ──
router.include_router(email_agent.router, tags=["Email Agent"])
router.include_router(email_resume_processor.router, tags=["Email Resume Processing"])
router.include_router(notification_hub.router, tags=["Notification Hub"])
router.include_router(mom_action_items.router, tags=["MOM & Action Items"])

# ── Admin Configuration (App + Company Level) ──
router.include_router(app_admin_config.router, tags=["App Admin Configuration"])
router.include_router(company_admin_config.router, tags=["Company Admin Configuration"])

# ── Financial Reports — P&L, Balance Sheet, AR/AP, Associate 360° ──
router.include_router(financial_reports.router, tags=["Financial Reports"])

# ── Agreements — MSA, NDA, SOW, PO, Templates, E-Signature ──
router.include_router(agreements.router, tags=["Agreements & E-Signature"])


@router.get("", tags=["Status"])
async def v1_status():
    """Get v1 API status with module inventory."""
    return {
        "status": "ready",
        "version": "2.0.0",
        "platform": "HR Automation Platform",
        "modules": {
            "core": ["auth", "dashboard", "reports", "analytics"],
            "pipeline": ["resumes", "matching", "interviews", "submissions", "offers", "negotiations"],
            "ai_agents": ["copilot", "conversations", "rediscovery", "job_posts"],
            "sourcing": ["harvest", "marketing"],
            "self_service": ["candidate_portal"],
            "contracts": ["contracts"],
            "network": ["suppliers", "referrals", "clients"],
            "messaging": ["messaging"],
            "financial": ["payments", "timesheets", "invoices"],
            "admin": ["alerts", "security", "admin", "cicd"],
            "vms_msp": ["organizations", "msp", "client_portal", "supplier_portal"],
            "vms_enhancement": ["rate_cards", "compliance_mgmt", "sla", "vms_timesheets", "auto_invoicing"],
            "candidate_crm": ["crm"],
            "ats_enhancement": ["ats"],
            "phase_4": ["search", "automation"],
            "bulk_operations": ["bulk_operations"],
        },
        "total_agents": 43,
        "total_api_modules": 43,
    }


logger.info("V1 router initialized with all 43 sub-routers (E2E Testing Agent added)")
