"""
Screening Feedback API — recruiter-level screening at application, import, and management time.

Prefix: /screening-feedback
"""

from __future__ import annotations
from fastapi import APIRouter, Query, Path
from datetime import datetime, timezone

router = APIRouter(prefix="/screening-feedback", tags=["Screening Feedback"])

# ═══════════════════════════════════════════════════════════════
# MOCK DATA
# ═══════════════════════════════════════════════════════════════

_now = datetime.now(timezone.utc).isoformat()

CHECKLISTS = [
    {
        "id": 1, "org_id": 1, "name": "Standard Application Screening",
        "description": "Default checklist for all incoming job applications",
        "is_default": True, "is_active": True,
        "applicable_to": ["application", "job_board", "referral"],
        "items": [
            {"id": 1, "checklist_id": 1, "category": "skills_match", "question_text": "Does the candidate possess the required primary skills listed in the job description?", "question_type": "rating_1_5", "weight": 2.0, "is_required": True, "is_eliminatory": True, "min_passing_score": 3, "display_order": 1, "help_text": "Rate 1-5 based on resume and profile match"},
            {"id": 2, "checklist_id": 1, "category": "experience_level", "question_text": "Does the candidate meet the minimum years of experience requirement?", "question_type": "yes_no", "weight": 1.5, "is_required": True, "is_eliminatory": True, "min_passing_score": 0, "display_order": 2, "help_text": "Check against job posting requirements"},
            {"id": 3, "checklist_id": 1, "category": "work_authorization", "question_text": "What is the candidate's work authorization status?", "question_type": "select", "options": ["US Citizen", "Green Card", "H1B", "H1B Transfer", "OPT/CPT", "EAD", "TN Visa", "L1", "Requires Sponsorship", "Unknown"], "weight": 2.0, "is_required": True, "is_eliminatory": False, "min_passing_score": 0, "display_order": 3, "help_text": "Verify legal right to work"},
            {"id": 4, "checklist_id": 1, "category": "location_fit", "question_text": "Is the candidate located in or willing to relocate to the required location?", "question_type": "select", "options": ["Local — no relocation needed", "Remote — approved location", "Willing to relocate", "Relocation required — candidate hesitant", "Location mismatch"], "weight": 1.5, "is_required": True, "is_eliminatory": False, "min_passing_score": 0, "display_order": 4, "help_text": "Consider remote, hybrid, on-site requirements"},
            {"id": 5, "checklist_id": 1, "category": "rate_fit", "question_text": "Is the candidate's expected rate/salary within the budgeted range?", "question_type": "rating_1_5", "weight": 1.5, "is_required": True, "is_eliminatory": False, "min_passing_score": 0, "display_order": 5, "help_text": "1 = way over budget, 5 = well within range"},
            {"id": 6, "checklist_id": 1, "category": "availability", "question_text": "When can the candidate start?", "question_type": "select", "options": ["Immediately", "Within 1 week", "Within 2 weeks", "Within 1 month", "More than 1 month", "Unknown"], "weight": 1.0, "is_required": True, "is_eliminatory": False, "min_passing_score": 0, "display_order": 6, "help_text": "Compare against client's urgency level"},
            {"id": 7, "checklist_id": 1, "category": "communication", "question_text": "Rate the candidate's communication quality (resume writing, initial correspondence)", "question_type": "rating_1_5", "weight": 1.0, "is_required": False, "is_eliminatory": False, "min_passing_score": 0, "display_order": 7, "help_text": "Based on resume, cover letter, or initial messages"},
            {"id": 8, "checklist_id": 1, "category": "education", "question_text": "Does the candidate meet the educational requirements?", "question_type": "yes_no", "weight": 0.5, "is_required": False, "is_eliminatory": False, "min_passing_score": 0, "display_order": 8, "help_text": "Check degree requirements if specified"},
            {"id": 9, "checklist_id": 1, "category": "overall", "question_text": "Overall impression and gut check — would you want to talk to this candidate?", "question_type": "rating_1_5", "weight": 1.5, "is_required": True, "is_eliminatory": False, "min_passing_score": 0, "display_order": 9, "help_text": "Your professional assessment based on all factors"},
            {"id": 10, "checklist_id": 1, "category": "background", "question_text": "Any red flags observed during initial screening?", "question_type": "free_text", "weight": 0, "is_required": False, "is_eliminatory": False, "min_passing_score": 0, "display_order": 10, "help_text": "Job hopping, gaps in employment, inconsistencies, etc."},
        ],
    },
    {
        "id": 2, "org_id": 1, "name": "Quick Import Screening",
        "description": "Lightweight screening for recruiter-imported or bulk-uploaded candidates",
        "is_default": False, "is_active": True,
        "applicable_to": ["manual_import", "resume_upload", "ai_sourced"],
        "items": [
            {"id": 11, "checklist_id": 2, "category": "skills_match", "question_text": "Primary technology match to open requirements", "question_type": "rating_1_5", "weight": 2.0, "is_required": True, "is_eliminatory": False, "min_passing_score": 0, "display_order": 1, "help_text": "How well do their skills align with what we're looking for?"},
            {"id": 12, "checklist_id": 2, "category": "experience_level", "question_text": "Experience level assessment (junior / mid / senior / lead)", "question_type": "select", "options": ["Junior (0-2 yrs)", "Mid (3-5 yrs)", "Senior (6-10 yrs)", "Lead/Principal (10+ yrs)"], "weight": 1.5, "is_required": True, "is_eliminatory": False, "min_passing_score": 0, "display_order": 2, "help_text": "Based on resume review"},
            {"id": 13, "checklist_id": 2, "category": "work_authorization", "question_text": "Work authorization status (if known)", "question_type": "select", "options": ["US Citizen", "Green Card", "H1B", "OPT/CPT", "EAD", "Requires Sponsorship", "Unknown"], "weight": 1.5, "is_required": False, "is_eliminatory": False, "min_passing_score": 0, "display_order": 3, "help_text": "Leave as Unknown if not available from resume"},
            {"id": 14, "checklist_id": 2, "category": "rate_fit", "question_text": "Estimated market rate alignment", "question_type": "rating_1_5", "weight": 1.0, "is_required": False, "is_eliminatory": False, "min_passing_score": 0, "display_order": 4, "help_text": "1 = likely too expensive, 5 = great value"},
            {"id": 15, "checklist_id": 2, "category": "overall", "question_text": "Priority level for outreach", "question_type": "select", "options": ["High — contact immediately", "Medium — add to pipeline", "Low — keep on file", "Skip — not a fit"], "weight": 1.5, "is_required": True, "is_eliminatory": False, "min_passing_score": 0, "display_order": 5, "help_text": "How urgently should we engage this candidate?"},
            {"id": 16, "checklist_id": 2, "category": "overall", "question_text": "Recruiter notes on candidate potential", "question_type": "free_text", "weight": 0, "is_required": False, "is_eliminatory": False, "min_passing_score": 0, "display_order": 6, "help_text": "Anything notable from initial profile review"},
        ],
    },
    {
        "id": 3, "org_id": 1, "name": "Compliance-Heavy Screening (Govt/Healthcare)",
        "description": "Extended screening for positions requiring compliance checks",
        "is_default": False, "is_active": True,
        "applicable_to": ["application", "manual_import"],
        "items": [
            {"id": 17, "checklist_id": 3, "category": "skills_match", "question_text": "Required certifications verified?", "question_type": "checklist", "options": ["Security Clearance", "HIPAA Training", "CompTIA Security+", "PMP", "AWS Certified", "Other"], "weight": 2.0, "is_required": True, "is_eliminatory": True, "min_passing_score": 0, "display_order": 1, "help_text": "Check all applicable certifications mentioned in resume"},
            {"id": 18, "checklist_id": 3, "category": "background", "question_text": "Background check eligibility", "question_type": "select", "options": ["Likely passes — clean history", "May have issues — needs review", "Known issues — discuss with manager", "Unknown"], "weight": 2.0, "is_required": True, "is_eliminatory": False, "min_passing_score": 0, "display_order": 2, "help_text": "Based on initial screening conversation"},
            {"id": 19, "checklist_id": 3, "category": "work_authorization", "question_text": "US Person status (for ITAR/export control compliance)", "question_type": "yes_no", "weight": 2.5, "is_required": True, "is_eliminatory": True, "min_passing_score": 0, "display_order": 3, "help_text": "Required for government-classified work"},
            {"id": 20, "checklist_id": 3, "category": "references", "question_text": "Can the candidate provide professional references?", "question_type": "yes_no", "weight": 1.0, "is_required": True, "is_eliminatory": False, "min_passing_score": 0, "display_order": 4, "help_text": "At least 2 professional references"},
            {"id": 21, "checklist_id": 3, "category": "overall", "question_text": "Compliance risk assessment", "question_type": "rating_1_5", "weight": 2.0, "is_required": True, "is_eliminatory": False, "min_passing_score": 3, "display_order": 5, "help_text": "1 = high risk, 5 = no concerns"},
        ],
    },
]

# Flatten items for lookup
_all_items = {item["id"]: item for cl in CHECKLISTS for item in cl["items"]}

FEEDBACK_RECORDS = [
    {
        "id": 1, "candidate_id": 1, "candidate_name": "Rajesh Kumar", "requirement_id": 101, "requirement_title": "Sr Python Developer", "checklist_id": 1,
        "screener_name": "Alice Morgan", "screener_email": "alice.morgan@company.com",
        "screening_source": "application",
        "overall_score": 78, "skills_score": 85, "experience_score": 80, "authorization_score": 55, "location_score": 80, "rate_score": 70, "availability_score": 90, "communication_score": 75,
        "decision": "proceed", "decision_reason": "Strong Python skills, H1B transfer manageable, good rate alignment",
        "decision_at": "2026-03-10T10:30:00Z",
        "summary_notes": "Solid backend developer with 8+ years. Python/SQL core strengths. H1B transfer required — verify timeline with immigration team. Rate expectation reasonable for experience level.",
        "strengths": ["Strong Python/SQL proficiency", "Relevant industry experience", "Good communication in initial screen"],
        "concerns": ["H1B transfer timeline may delay start", "Limited React experience for full-stack reqs"],
        "red_flags": [],
        "is_draft": False, "completed_at": "2026-03-10T10:45:00Z", "duration_minutes": 15,
        "created_at": "2026-03-10T10:30:00Z",
        "answers": [
            {"id": 1, "checklist_item_id": 1, "answer_rating": 4, "score": 80, "is_passing": True, "evaluator_notes": "Python, SQL, AWS — matches 3 of 4 required skills"},
            {"id": 2, "checklist_item_id": 2, "answer_yes_no": True, "score": 100, "is_passing": True, "evaluator_notes": "8 years total, 6 in Python"},
            {"id": 3, "checklist_item_id": 3, "answer_choice": "H1B Transfer", "score": 55, "is_passing": True, "evaluator_notes": "Currently on H1B, employer willing to transfer"},
            {"id": 4, "checklist_item_id": 4, "answer_choice": "Remote — approved location", "score": 80, "is_passing": True, "evaluator_notes": "Based in TX, role is remote-first"},
            {"id": 5, "checklist_item_id": 5, "answer_rating": 4, "score": 80, "is_passing": True, "evaluator_notes": "Asking $75/hr, budget is $80/hr"},
            {"id": 6, "checklist_item_id": 6, "answer_choice": "Within 2 weeks", "score": 80, "is_passing": True, "evaluator_notes": "2-week notice period"},
            {"id": 7, "checklist_item_id": 7, "answer_rating": 4, "score": 80, "is_passing": True, "evaluator_notes": "Well-structured resume, clear cover letter"},
            {"id": 8, "checklist_item_id": 8, "answer_yes_no": True, "score": 100, "is_passing": True, "evaluator_notes": "MS in CS from reputable university"},
            {"id": 9, "checklist_item_id": 9, "answer_rating": 4, "score": 80, "is_passing": True, "evaluator_notes": "Good overall impression, worth pursuing"},
            {"id": 10, "checklist_item_id": 10, "answer_text": "No red flags. Clean employment history.", "score": 0, "is_passing": True, "evaluator_notes": ""},
        ],
    },
    {
        "id": 2, "candidate_id": 2, "candidate_name": "Emily Chen", "requirement_id": 101, "requirement_title": "Sr Python Developer", "checklist_id": 1,
        "screener_name": "Alice Morgan", "screener_email": "alice.morgan@company.com",
        "screening_source": "application",
        "overall_score": 92, "skills_score": 95, "experience_score": 90, "authorization_score": 100, "location_score": 100, "rate_score": 80, "availability_score": 80, "communication_score": 95,
        "decision": "shortlist", "decision_reason": "Exceptional candidate — US Citizen, strong technical match, excellent communication",
        "decision_at": "2026-03-10T11:00:00Z",
        "summary_notes": "Outstanding profile. 10+ years Python, strong system design. US Citizen — no work auth issues. Currently employed, needs 3-week notice but flexible on start. Slight premium on rate but justified.",
        "strengths": ["Exceptional Python/System Design skills", "US Citizen — no sponsorship needed", "Excellent written communication", "Leadership experience"],
        "concerns": ["Rate slightly above midpoint", "3-week notice period"],
        "red_flags": [],
        "is_draft": False, "completed_at": "2026-03-10T11:12:00Z", "duration_minutes": 12,
        "created_at": "2026-03-10T10:48:00Z",
        "answers": [
            {"id": 11, "checklist_item_id": 1, "answer_rating": 5, "score": 100, "is_passing": True, "evaluator_notes": "All 4 required skills + extras (Docker, K8s)"},
            {"id": 12, "checklist_item_id": 2, "answer_yes_no": True, "score": 100, "is_passing": True, "evaluator_notes": "10+ years, exceeds minimum"},
            {"id": 13, "checklist_item_id": 3, "answer_choice": "US Citizen", "score": 100, "is_passing": True, "evaluator_notes": "No work authorization concerns"},
            {"id": 14, "checklist_item_id": 4, "answer_choice": "Local — no relocation needed", "score": 100, "is_passing": True, "evaluator_notes": "Already in required metro area"},
            {"id": 15, "checklist_item_id": 5, "answer_rating": 4, "score": 80, "is_passing": True, "evaluator_notes": "Asking $85/hr vs $80 budget — negotiable"},
            {"id": 16, "checklist_item_id": 6, "answer_choice": "Within 1 month", "score": 60, "is_passing": True, "evaluator_notes": "3-week notice, could be sooner"},
            {"id": 17, "checklist_item_id": 7, "answer_rating": 5, "score": 100, "is_passing": True, "evaluator_notes": "Polished, professional, articulate"},
            {"id": 18, "checklist_item_id": 8, "answer_yes_no": True, "score": 100, "is_passing": True, "evaluator_notes": "MS CS — top 20 program"},
            {"id": 19, "checklist_item_id": 9, "answer_rating": 5, "score": 100, "is_passing": True, "evaluator_notes": "Top candidate — fast-track"},
            {"id": 20, "checklist_item_id": 10, "answer_text": "None. Consistent career progression.", "score": 0, "is_passing": True, "evaluator_notes": ""},
        ],
    },
    {
        "id": 3, "candidate_id": 3, "candidate_name": "Marcus Johnson", "requirement_id": 102, "requirement_title": "React Developer", "checklist_id": 1,
        "screener_name": "Bob Chen", "screener_email": "bob.chen@company.com",
        "screening_source": "referral",
        "overall_score": 58, "skills_score": 70, "experience_score": 60, "authorization_score": 40, "location_score": 60, "rate_score": 65, "availability_score": 80, "communication_score": 60,
        "decision": "hold", "decision_reason": "Skills match is decent but OPT expiring soon — immigration risk needs clarification",
        "decision_at": "2026-03-11T14:20:00Z",
        "summary_notes": "Junior-mid level React developer referred by team member. OPT status expiring in 4 months — would need H1B sponsorship. Skills are adequate but not exceptional. Hold pending immigration clarification.",
        "strengths": ["React/TypeScript fundamentals", "Referred by trusted team member", "Available immediately"],
        "concerns": ["OPT expiring — sponsorship needed", "Limited professional experience (3 yrs)", "No backend experience"],
        "red_flags": ["OPT expiration in 4 months without H1B petition filed"],
        "is_draft": False, "completed_at": "2026-03-11T14:35:00Z", "duration_minutes": 15,
        "created_at": "2026-03-11T14:15:00Z",
        "answers": [
            {"id": 21, "checklist_item_id": 1, "answer_rating": 3, "score": 60, "is_passing": True, "evaluator_notes": "React yes, but limited depth in state mgmt/testing"},
            {"id": 22, "checklist_item_id": 2, "answer_yes_no": True, "score": 60, "is_passing": True, "evaluator_notes": "3 years — meets minimum but barely"},
            {"id": 23, "checklist_item_id": 3, "answer_choice": "OPT/CPT", "score": 40, "is_passing": True, "evaluator_notes": "OPT — expiring Aug 2026"},
            {"id": 24, "checklist_item_id": 4, "answer_choice": "Relocation required — candidate hesitant", "score": 40, "is_passing": True, "evaluator_notes": "In different state, hybrid role requires some onsite"},
            {"id": 25, "checklist_item_id": 5, "answer_rating": 3, "score": 60, "is_passing": True, "evaluator_notes": "Rate reasonable for experience level"},
            {"id": 26, "checklist_item_id": 6, "answer_choice": "Immediately", "score": 100, "is_passing": True, "evaluator_notes": "Currently between contracts"},
            {"id": 27, "checklist_item_id": 9, "answer_rating": 3, "score": 60, "is_passing": True, "evaluator_notes": "Decent but immigration risk is concerning"},
        ],
    },
    {
        "id": 4, "candidate_id": 4, "candidate_name": "Sarah Williams", "requirement_id": None, "requirement_title": None, "checklist_id": 2,
        "screener_name": "Alice Morgan", "screener_email": "alice.morgan@company.com",
        "screening_source": "manual_import",
        "overall_score": 82, "skills_score": 90, "experience_score": 85, "authorization_score": 100, "location_score": 80, "rate_score": 75, "availability_score": 60, "communication_score": 80,
        "decision": "proceed", "decision_reason": "Strong frontend lead profile imported from LinkedIn — assign to open React/Lead reqs",
        "decision_at": "2026-03-12T09:15:00Z",
        "summary_notes": "Imported from LinkedIn sourcing. 12 years frontend experience, 5 years leading teams. US Citizen. Currently employed — will need 1 month notice. Assign to REQ-102 or REQ-105.",
        "strengths": ["12 years frontend experience", "Team leadership background", "US Citizen", "Strong portfolio"],
        "concerns": ["1 month notice period", "Rate may be high for current budget"],
        "red_flags": [],
        "is_draft": False, "completed_at": "2026-03-12T09:22:00Z", "duration_minutes": 7,
        "created_at": "2026-03-12T09:10:00Z",
        "answers": [
            {"id": 28, "checklist_item_id": 11, "answer_rating": 5, "score": 100, "is_passing": True, "evaluator_notes": "React, TypeScript, Next.js, team leadership"},
            {"id": 29, "checklist_item_id": 12, "answer_choice": "Lead/Principal (10+ yrs)", "score": 100, "is_passing": True, "evaluator_notes": "12 years total"},
            {"id": 30, "checklist_item_id": 13, "answer_choice": "US Citizen", "score": 100, "is_passing": True, "evaluator_notes": ""},
            {"id": 31, "checklist_item_id": 14, "answer_rating": 3, "score": 60, "is_passing": True, "evaluator_notes": "Premium rate expected for lead level"},
            {"id": 32, "checklist_item_id": 15, "answer_choice": "High — contact immediately", "score": 100, "is_passing": True, "evaluator_notes": "Great fit for multiple open reqs"},
            {"id": 33, "checklist_item_id": 16, "answer_text": "Strong LinkedIn presence. Multiple endorsements for React/TS. Published technical blog posts.", "score": 0, "is_passing": True, "evaluator_notes": ""},
        ],
    },
    {
        "id": 5, "candidate_id": 5, "candidate_name": "David Park", "requirement_id": 103, "requirement_title": "Data Engineer", "checklist_id": 1,
        "screener_name": "Bob Chen", "screener_email": "bob.chen@company.com",
        "screening_source": "job_board",
        "overall_score": 45, "skills_score": 50, "experience_score": 40, "authorization_score": 60, "location_score": 80, "rate_score": 90, "availability_score": 100, "communication_score": 40,
        "decision": "reject", "decision_reason": "Insufficient experience for senior role. Resume has inconsistencies.",
        "decision_at": "2026-03-12T16:00:00Z",
        "summary_notes": "Applied via Indeed for Sr Data Engineer role. Only 2 years experience — doesn't meet 5-year minimum. Resume lists technologies not reflected in job descriptions. Communication quality low — multiple typos in cover letter.",
        "strengths": ["Available immediately", "Rate within budget"],
        "concerns": ["Experience far below requirement", "Technology claims don't match work history"],
        "red_flags": ["Resume inconsistencies — claims 5 years Spark but only 2 years out of school", "Poor attention to detail in application"],
        "is_draft": False, "completed_at": "2026-03-12T16:08:00Z", "duration_minutes": 8,
        "created_at": "2026-03-12T15:55:00Z",
        "answers": [
            {"id": 34, "checklist_item_id": 1, "answer_rating": 2, "score": 40, "is_passing": False, "evaluator_notes": "Claims skills not supported by experience"},
            {"id": 35, "checklist_item_id": 2, "answer_yes_no": False, "score": 0, "is_passing": False, "evaluator_notes": "2 years vs 5 year minimum"},
            {"id": 36, "checklist_item_id": 3, "answer_choice": "EAD", "score": 60, "is_passing": True, "evaluator_notes": "EAD through spouse"},
            {"id": 37, "checklist_item_id": 9, "answer_rating": 2, "score": 40, "is_passing": False, "evaluator_notes": "Not suitable for this role level"},
            {"id": 38, "checklist_item_id": 10, "answer_text": "Resume inconsistencies — experience claims don't match timeline. Multiple typos in cover letter.", "score": 0, "is_passing": False, "evaluator_notes": "Red flag"},
        ],
    },
    {
        "id": 6, "candidate_id": 6, "candidate_name": "Priya Sharma", "requirement_id": 101, "requirement_title": "Sr Python Developer", "checklist_id": 1,
        "screener_name": "Alice Morgan", "screener_email": "alice.morgan@company.com",
        "screening_source": "application",
        "overall_score": 0, "skills_score": 0, "experience_score": 0, "authorization_score": 0, "location_score": 0, "rate_score": 0, "availability_score": 0, "communication_score": 0,
        "decision": "pending", "decision_reason": None,
        "decision_at": None,
        "summary_notes": "",
        "strengths": [], "concerns": [], "red_flags": [],
        "is_draft": True, "completed_at": None, "duration_minutes": None,
        "created_at": "2026-03-14T08:00:00Z",
        "answers": [],
    },
]


# ═══════════════════════════════════════════════════════════════
# CHECKLIST ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/checklists")
async def list_checklists(source: str | None = Query(None)):
    """List all screening checklists, optionally filtered by applicable source."""
    results = CHECKLISTS
    if source:
        results = [c for c in results if source in c.get("applicable_to", [])]
    return {"checklists": results, "total": len(results)}


@router.get("/checklists/{checklist_id}")
async def get_checklist(checklist_id: int = Path(...)):
    cl = next((c for c in CHECKLISTS if c["id"] == checklist_id), None)
    if not cl:
        return {"error": "Not found"}, 404
    return cl


@router.post("/checklists")
async def create_checklist(data: dict | None = None):
    new_id = max(c["id"] for c in CHECKLISTS) + 1
    return {"id": new_id, "message": "Checklist created", "created_at": _now}


@router.put("/checklists/{checklist_id}")
async def update_checklist(checklist_id: int = Path(...)):
    return {"id": checklist_id, "message": "Checklist updated", "updated_at": _now}


# ═══════════════════════════════════════════════════════════════
# SCREENING FEEDBACK RECORDS
# ═══════════════════════════════════════════════════════════════

@router.get("/records")
async def list_feedback_records(
    candidate_id: int | None = Query(None),
    requirement_id: int | None = Query(None),
    decision: str | None = Query(None),
    source: str | None = Query(None),
    is_draft: bool | None = Query(None),
):
    """List screening feedback records with filters."""
    results = FEEDBACK_RECORDS
    if candidate_id:
        results = [r for r in results if r["candidate_id"] == candidate_id]
    if requirement_id:
        results = [r for r in results if r["requirement_id"] == requirement_id]
    if decision:
        results = [r for r in results if r["decision"] == decision]
    if source:
        results = [r for r in results if r["screening_source"] == source]
    if is_draft is not None:
        results = [r for r in results if r["is_draft"] == is_draft]
    return {"records": results, "total": len(results)}


@router.get("/records/{record_id}")
async def get_feedback_record(record_id: int = Path(...)):
    rec = next((r for r in FEEDBACK_RECORDS if r["id"] == record_id), None)
    if not rec:
        return {"error": "Not found"}, 404
    return rec


@router.post("/records")
async def create_feedback_record(data: dict | None = None):
    """Create a new screening feedback record (scenario 1: application, 2: import, 3: manual)."""
    new_id = max(r["id"] for r in FEEDBACK_RECORDS) + 1
    return {"id": new_id, "message": "Screening feedback record created", "is_draft": True, "created_at": _now}


@router.put("/records/{record_id}")
async def update_feedback_record(record_id: int = Path(...), data: dict | None = None):
    """Update an existing screening feedback record (edit scenario)."""
    return {"id": record_id, "message": "Screening feedback updated", "updated_at": _now}


@router.post("/records/{record_id}/complete")
async def complete_feedback_record(record_id: int = Path(...)):
    """Finalize screening feedback — computes final scores and marks as non-draft."""
    rec = next((r for r in FEEDBACK_RECORDS if r["id"] == record_id), None)
    if not rec:
        return {"error": "Not found"}, 404
    return {"id": record_id, "message": "Screening feedback completed", "overall_score": rec["overall_score"], "decision": rec["decision"], "completed_at": _now}


@router.delete("/records/{record_id}")
async def delete_feedback_record(record_id: int = Path(...)):
    return {"id": record_id, "message": "Screening feedback deleted"}


# ═══════════════════════════════════════════════════════════════
# ANSWERS
# ═══════════════════════════════════════════════════════════════

@router.post("/records/{record_id}/answers")
async def submit_answers(record_id: int = Path(...), data: dict | None = None):
    """Submit or update answers for a screening feedback record."""
    return {"record_id": record_id, "message": "Answers saved", "updated_at": _now}


@router.get("/records/{record_id}/answers")
async def get_answers(record_id: int = Path(...)):
    rec = next((r for r in FEEDBACK_RECORDS if r["id"] == record_id), None)
    if not rec:
        return {"error": "Not found"}, 404
    return {"record_id": record_id, "answers": rec.get("answers", []), "total": len(rec.get("answers", []))}


# ═══════════════════════════════════════════════════════════════
# DECISION
# ═══════════════════════════════════════════════════════════════

@router.post("/records/{record_id}/decide")
async def make_decision(record_id: int = Path(...), data: dict | None = None):
    """Record screening decision (proceed, hold, reject, shortlist, needs_review)."""
    return {"record_id": record_id, "message": "Decision recorded", "decision_at": _now}


# ═══════════════════════════════════════════════════════════════
# CANDIDATE SCREENING HISTORY
# ═══════════════════════════════════════════════════════════════

@router.get("/candidate/{candidate_id}/history")
async def get_candidate_screening_history(candidate_id: int = Path(...)):
    """Get all screening feedback records for a candidate across all requirements."""
    records = [r for r in FEEDBACK_RECORDS if r["candidate_id"] == candidate_id]
    return {
        "candidate_id": candidate_id,
        "total_screenings": len(records),
        "records": records,
        "latest_decision": records[-1]["decision"] if records else None,
        "latest_score": records[-1]["overall_score"] if records else None,
    }


@router.get("/requirement/{requirement_id}/screenings")
async def get_requirement_screenings(requirement_id: int = Path(...)):
    """Get all screening feedback for a specific requirement — ranked by score."""
    records = sorted(
        [r for r in FEEDBACK_RECORDS if r["requirement_id"] == requirement_id],
        key=lambda r: r["overall_score"],
        reverse=True,
    )
    return {
        "requirement_id": requirement_id,
        "total": len(records),
        "records": records,
        "summary": {
            "proceed": len([r for r in records if r["decision"] == "proceed"]),
            "shortlist": len([r for r in records if r["decision"] == "shortlist"]),
            "hold": len([r for r in records if r["decision"] == "hold"]),
            "reject": len([r for r in records if r["decision"] == "reject"]),
            "pending": len([r for r in records if r["decision"] == "pending"]),
        },
    }


# ═══════════════════════════════════════════════════════════════
# DASHBOARD / STATS
# ═══════════════════════════════════════════════════════════════

@router.get("/dashboard")
async def screening_dashboard():
    """Screening analytics overview."""
    completed = [r for r in FEEDBACK_RECORDS if not r["is_draft"]]
    return {
        "total_screenings": len(FEEDBACK_RECORDS),
        "completed": len(completed),
        "pending_draft": len(FEEDBACK_RECORDS) - len(completed),
        "avg_score": round(sum(r["overall_score"] for r in completed) / max(len(completed), 1), 1),
        "avg_duration_minutes": round(sum(r["duration_minutes"] or 0 for r in completed) / max(len(completed), 1), 1),
        "by_decision": {
            "proceed": len([r for r in completed if r["decision"] == "proceed"]),
            "shortlist": len([r for r in completed if r["decision"] == "shortlist"]),
            "hold": len([r for r in completed if r["decision"] == "hold"]),
            "reject": len([r for r in completed if r["decision"] == "reject"]),
            "needs_review": len([r for r in completed if r["decision"] == "needs_review"]),
        },
        "by_source": {
            "application": len([r for r in completed if r["screening_source"] == "application"]),
            "manual_import": len([r for r in completed if r["screening_source"] == "manual_import"]),
            "referral": len([r for r in completed if r["screening_source"] == "referral"]),
            "job_board": len([r for r in completed if r["screening_source"] == "job_board"]),
        },
        "top_screeners": [
            {"name": "Alice Morgan", "screenings": 3, "avg_score": 84, "avg_minutes": 11},
            {"name": "Bob Chen", "screenings": 2, "avg_score": 52, "avg_minutes": 12},
        ],
        "recent_activity": [
            {"candidate": "Priya Sharma", "requirement": "Sr Python Developer", "status": "draft", "date": "2026-03-14"},
            {"candidate": "David Park", "requirement": "Data Engineer", "status": "rejected", "date": "2026-03-12"},
            {"candidate": "Sarah Williams", "requirement": None, "status": "proceed (import)", "date": "2026-03-12"},
            {"candidate": "Marcus Johnson", "requirement": "React Developer", "status": "hold", "date": "2026-03-11"},
        ],
    }
