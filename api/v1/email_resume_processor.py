"""Email Resume Processor API — capture resumes from emails, parse, match, and add to platform."""
from datetime import datetime
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/email-resume")


# ══════════════════════════════════════════════════════════════
#  MOCK DATA
# ══════════════════════════════════════════════════════════════

_mock_captures = [
    {
        "id": 1, "email_message_id": 2,
        "candidate_name": "Priya Sharma", "candidate_email": "priya.sharma@gmail.com",
        "candidate_phone": "+1-408-555-0147", "source_type": "email_attachment",
        "attachment_filename": "PriyaSharma_Resume.pdf", "attachment_size_bytes": 245000,
        "parsed_successfully": True,
        "skills_extracted": ["Python", "Django", "FastAPI", "AWS", "PostgreSQL", "Docker", "Kubernetes", "Redis", "Celery", "React"],
        "experience_years": 8.0, "education_level": "M.S. Computer Science",
        "current_title": "Senior Software Engineer", "current_company": "DataFlow Inc.",
        "matched_requirement_id": 1042,
        "match_score": 87.5, "match_level": "strong",
        "match_breakdown": {"skills": 92, "experience": 88, "education": 85, "location": 80, "culture_fit": 82, "overall": 87.5},
        "recommendation": "strong_yes",
        "recommendation_notes": "Excellent match for Senior Python Developer role. 8 years experience with strong backend skills. Django/FastAPI expertise directly applicable. AWS certified. Only gap: no Go experience listed but Python proficiency compensates.",
        "added_to_platform": True, "candidate_id_created": 2847,
        "added_at": "2026-03-13T07:32:00Z", "review_status": "pending",
        "email_subject": "New application: Priya Sharma applied for Senior Python Developer",
        "email_from": "apply+candidate@jobs.linkedin.com",
    },
    {
        "id": 2, "email_message_id": 5,
        "candidate_name": "Amit Patel", "candidate_email": "amit.patel@gmail.com",
        "candidate_phone": "+1-512-555-0234", "source_type": "email_attachment",
        "attachment_filename": "AmitPatel_CV.pdf", "attachment_size_bytes": 198000,
        "parsed_successfully": True,
        "skills_extracted": ["React Native", "JavaScript", "TypeScript", "iOS", "Android", "Redux", "GraphQL", "Firebase", "Node.js", "Jest"],
        "experience_years": 5.5, "education_level": "B.Tech Computer Science",
        "current_title": "Mobile Developer", "current_company": "AppWorks Studio",
        "matched_requirement_id": 1048,
        "match_score": 72.0, "match_level": "good",
        "match_breakdown": {"skills": 85, "experience": 68, "education": 65, "location": 70, "culture_fit": 75, "overall": 72.0},
        "recommendation": "yes",
        "recommendation_notes": "Good match for React Native Developer. 5+ years mobile experience with strong React Native/TypeScript skills. Could benefit from more enterprise-scale experience. Worth interviewing.",
        "added_to_platform": True, "candidate_id_created": 2848,
        "added_at": "2026-03-13T05:22:00Z", "review_status": "pending",
        "email_subject": "Application for React Native Developer Position",
        "email_from": "amit.patel@gmail.com",
    },
    {
        "id": 3, "email_message_id": None,
        "candidate_name": "Deepa Krishnan", "candidate_email": "deepa.k@outlook.com",
        "candidate_phone": "+1-650-555-0189", "source_type": "email_attachment",
        "attachment_filename": "DeepaKrishnan_Resume_2026.pdf", "attachment_size_bytes": 312000,
        "parsed_successfully": True,
        "skills_extracted": ["Java", "Spring Boot", "Microservices", "Kafka", "AWS", "Docker", "Jenkins", "MongoDB", "Oracle", "Agile"],
        "experience_years": 10.0, "education_level": "M.S. Software Engineering",
        "current_title": "Lead Software Engineer", "current_company": "CloudSphere Systems",
        "matched_requirement_id": None,
        "match_score": None, "match_level": None,
        "match_breakdown": None,
        "recommendation": None,
        "recommendation_notes": "Strong Java developer profile. No matching open requirement at this time. Added to talent pool for future Java positions.",
        "added_to_platform": True, "candidate_id_created": 2849,
        "added_at": "2026-03-12T16:00:00Z", "review_status": "pending",
        "email_subject": "Referral: Deepa Krishnan - Java/Spring Boot Expert",
        "email_from": "referrals@staffpro.com",
    },
    {
        "id": 4, "email_message_id": None,
        "candidate_name": "Carlos Rivera", "candidate_email": "c.rivera@yahoo.com",
        "candidate_phone": None, "source_type": "email_attachment",
        "attachment_filename": "resume_carlos_r.docx", "attachment_size_bytes": 89000,
        "parsed_successfully": True,
        "skills_extracted": ["Data Engineering", "Python", "Spark", "Snowflake", "dbt", "Airflow", "SQL", "Terraform", "GCP", "BigQuery"],
        "experience_years": 6.0, "education_level": "B.S. Data Science",
        "current_title": "Data Engineer", "current_company": "InsightPro Analytics",
        "matched_requirement_id": 1044,
        "match_score": 91.0, "match_level": "excellent",
        "match_breakdown": {"skills": 95, "experience": 85, "education": 88, "location": 92, "culture_fit": 90, "overall": 91.0},
        "recommendation": "strong_yes",
        "recommendation_notes": "Excellent match for Data Engineer role at TechCorp. 6 years with Spark/Snowflake/dbt — exact tech stack match. GCP + Terraform experience is a bonus. Recommend expedited interview.",
        "added_to_platform": True, "candidate_id_created": 2850,
        "added_at": "2026-03-12T11:00:00Z", "review_status": "approved",
        "email_subject": "Candidate Submission: Carlos Rivera for Data Engineer - TechCorp",
        "email_from": "michael.chen@staffpro.com",
    },
]


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Resume Captures
# ══════════════════════════════════════════════════════════════

@router.get("/captures")
async def get_resume_captures(
    match_level: Optional[str] = None,
    recommendation: Optional[str] = None,
    review_status: Optional[str] = None,
    added_to_platform: Optional[bool] = None,
    limit: int = Query(default=50, le=200),
):
    """Get all email-sourced resume captures with match scoring."""
    results = _mock_captures
    if match_level:
        results = [r for r in results if r.get("match_level") == match_level]
    if recommendation:
        results = [r for r in results if r.get("recommendation") == recommendation]
    if review_status:
        results = [r for r in results if r.get("review_status") == review_status]
    if added_to_platform is not None:
        results = [r for r in results if r["added_to_platform"] == added_to_platform]
    return {"items": results[:limit], "total": len(results)}


@router.get("/captures/{capture_id}")
async def get_resume_capture(capture_id: int):
    """Get detailed resume capture with full match breakdown."""
    capture = next((c for c in _mock_captures if c["id"] == capture_id), None)
    if not capture:
        return {"error": "Resume capture not found"}
    return capture


@router.post("/captures/{capture_id}/match")
async def run_match_scoring(capture_id: int, requirement_id: Optional[int] = None):
    """Run or re-run match scoring against a specific requirement or all open requirements."""
    capture = next((c for c in _mock_captures if c["id"] == capture_id), None)
    if not capture:
        return {"error": "Resume capture not found"}
    return {
        "capture_id": capture_id,
        "matched_requirements": [
            {"requirement_id": 1042, "title": "Senior Python Developer", "match_score": 87.5, "match_level": "strong"},
            {"requirement_id": 1044, "title": "Data Engineer", "match_score": 45.0, "match_level": "fair"},
            {"requirement_id": 1048, "title": "React Native Developer", "match_score": 32.0, "match_level": "poor"},
        ] if not requirement_id else [
            {"requirement_id": requirement_id, "match_score": 78.0, "match_level": "strong"}
        ],
    }


@router.post("/captures/{capture_id}/add-to-platform")
async def add_to_platform(capture_id: int):
    """Add parsed resume to the HotGigs candidate database."""
    return {
        "capture_id": capture_id, "candidate_id": 2851,
        "status": "added", "message": "Candidate added to platform successfully",
    }


@router.put("/captures/{capture_id}/review")
async def review_capture(capture_id: int, status: str = "approved", notes: Optional[str] = None):
    """Review a resume capture — approve, reject, or request more info."""
    return {"capture_id": capture_id, "review_status": status, "notes": notes, "reviewed_at": datetime.utcnow().isoformat()}


@router.post("/process-email/{email_id}")
async def process_email_resume(email_id: int):
    """Process an email to extract and parse any attached resumes."""
    return {
        "email_id": email_id, "resumes_found": 1,
        "captures_created": [{"id": 10, "filename": "resume.pdf", "parsed": True, "match_score": 75.0}],
    }


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Match Analytics & Stats
# ══════════════════════════════════════════════════════════════

@router.get("/stats")
async def get_resume_processing_stats():
    """Get resume processing statistics."""
    return {
        "total_captures": 47, "this_week": 12, "today": 2,
        "by_source": {"email_attachment": 28, "linkedin": 12, "direct_application": 5, "referral": 2},
        "by_match_level": {"excellent": 8, "strong": 15, "good": 12, "fair": 8, "poor": 4},
        "by_recommendation": {"strong_yes": 10, "yes": 14, "maybe": 12, "no": 11},
        "by_review_status": {"pending": 18, "approved": 22, "rejected": 7},
        "avg_match_score": 68.5, "added_to_platform_rate": 0.78,
        "top_matching_requirements": [
            {"id": 1042, "title": "Senior Python Developer", "matches": 6, "avg_score": 79.2},
            {"id": 1044, "title": "Data Engineer - TechCorp", "matches": 4, "avg_score": 82.1},
            {"id": 1048, "title": "React Native Developer", "matches": 3, "avg_score": 71.5},
        ],
    }


@router.get("/dashboard")
async def get_resume_dashboard():
    """Get resume processing dashboard data."""
    return {
        "kpis": {
            "captures_today": 2, "pending_review": 18,
            "strong_matches": 23, "added_this_week": 10,
            "avg_match_score": 68.5, "processing_time_avg_sec": 4.2,
        },
        "recent_captures": _mock_captures[:4],
        "top_candidates": [
            {"name": "Carlos Rivera", "match_score": 91.0, "requirement": "Data Engineer", "recommendation": "strong_yes"},
            {"name": "Priya Sharma", "match_score": 87.5, "requirement": "Senior Python Developer", "recommendation": "strong_yes"},
        ],
        "pipeline_funnel": {
            "emails_received": 120, "resumes_detected": 47,
            "parsed_successfully": 45, "matched": 39,
            "added_to_platform": 37, "approved": 22,
        },
    }
