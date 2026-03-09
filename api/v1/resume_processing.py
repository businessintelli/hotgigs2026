"""
Resume Processing API Router.

Features:
1. Resume preview thumbnails for applicant cards
2. DOCX-to-PDF conversion on upload
3. Resume download/view tracking
4. AI-powered resume condensation to 3 pages
"""

import logging
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, status
from pydantic import BaseModel

from schemas.resume_processing import (
    ThumbnailResponse,
    ThumbnailBatchResponse,
    ConversionResponse,
    ConversionBatchResponse,
    DownloadTrackRequest,
    DownloadLogResponse,
    DownloadAnalytics,
    RecruiterAccessReport,
    CondenseRequest,
    CondensedResumeResponse,
    ResumeHighlightsCard,
    ResumeProcessingStats,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume-processing", tags=["Resume Processing"])


# ═══════════════════════════════════════════════════════════════════════════
# MOCK DATA GENERATORS
# ═══════════════════════════════════════════════════════════════════════════

SAMPLE_CANDIDATES = [
    {"id": 1, "name": "Sarah Chen", "role": "Senior Software Engineer", "exp": 8, "skills": ["Python", "React", "AWS", "Docker", "PostgreSQL"], "education": "MS Computer Science, Stanford", "certs": 3, "achievements": ["Led migration to microservices saving $200K/yr", "Built ML pipeline processing 2M records/day", "Mentored 12 junior developers"]},
    {"id": 2, "name": "James Rodriguez", "role": "Data Scientist", "exp": 6, "skills": ["Python", "TensorFlow", "SQL", "Spark", "Tableau"], "education": "PhD Statistics, MIT", "certs": 2, "achievements": ["Published 4 ML research papers", "Built fraud detection model saving $5M annually", "Reduced model training time by 70%"]},
    {"id": 3, "name": "Priya Sharma", "role": "Product Manager", "exp": 10, "skills": ["Agile", "JIRA", "SQL", "Figma", "A/B Testing"], "education": "MBA, Wharton", "certs": 4, "achievements": ["Grew product ARR from $2M to $15M", "Launched 3 products from 0→1", "Led cross-functional team of 25"]},
    {"id": 4, "name": "Michael Kim", "role": "DevOps Engineer", "exp": 5, "skills": ["Kubernetes", "Terraform", "CI/CD", "AWS", "Python"], "education": "BS Computer Engineering, Georgia Tech", "certs": 5, "achievements": ["Reduced deployment time from 2hr to 8min", "Achieved 99.99% uptime SLA", "Automated infrastructure saving 40 eng-hours/week"]},
    {"id": 5, "name": "Emily Watson", "role": "Full Stack Developer", "exp": 4, "skills": ["TypeScript", "React", "Node.js", "GraphQL", "MongoDB"], "education": "BS Software Engineering, CMU", "certs": 2, "achievements": ["Built real-time collaboration feature for 50K users", "Reduced page load time by 60%", "Open source contributor with 2K+ GitHub stars"]},
    {"id": 6, "name": "David Okafor", "role": "Cloud Architect", "exp": 12, "skills": ["AWS", "Azure", "GCP", "Terraform", "Security"], "education": "MS Cloud Computing, Georgia Tech", "certs": 7, "achievements": ["Designed multi-cloud architecture for Fortune 500", "Reduced cloud spend by 35% ($1.2M)", "Led SOC2 and ISO27001 compliance"]},
    {"id": 7, "name": "Lisa Tanaka", "role": "ML Engineer", "exp": 7, "skills": ["PyTorch", "Python", "MLOps", "Kubernetes", "NLP"], "education": "MS AI, Carnegie Mellon", "certs": 3, "achievements": ["Deployed 15+ production ML models", "Built NLP pipeline for 20 languages", "Reduced model inference latency by 80%"]},
    {"id": 8, "name": "Alex Petrov", "role": "Backend Engineer", "exp": 9, "skills": ["Go", "Python", "gRPC", "Redis", "PostgreSQL"], "education": "BS Computer Science, UC Berkeley", "certs": 2, "achievements": ["Built event-driven system handling 100K events/sec", "Designed microservices for 10M+ daily users", "Reduced API latency P99 from 500ms to 50ms"]},
]

RECRUITERS = [
    {"id": 1, "name": "Tom Brady", "email": "tom.brady@hotgigs.com"},
    {"id": 2, "name": "Anna Lopez", "email": "anna.lopez@hotgigs.com"},
    {"id": 3, "name": "Chris Park", "email": "chris.park@hotgigs.com"},
    {"id": 4, "name": "Diana Wells", "email": "diana.wells@hotgigs.com"},
    {"id": 5, "name": "Raj Patel", "email": "raj.patel@hotgigs.com"},
]


def _mock_thumbnail(cand: dict, resume_id: int) -> dict:
    preview = f"{cand['name']} — {cand['role']}\n{cand['exp']} years experience\n\nSkills: {', '.join(cand['skills'][:4])}\n\nEducation: {cand['education']}\n\nKey Achievements:\n" + "\n".join(f"• {a}" for a in cand['achievements'][:2])
    return {
        "resume_id": resume_id,
        "thumbnail_url": f"/api/v1/resume-processing/thumbnail/{resume_id}/image",
        "thumbnail_format": "png",
        "width": 200,
        "height": 280,
        "page_count": max(1, cand["exp"] // 3),
        "preview_text": preview[:500],
        "generated_at": datetime.now().isoformat(),
    }


def _mock_condensed(cand: dict, resume_id: int) -> dict:
    orig_pages = max(2, cand["exp"] // 2)
    return {
        "resume_id": resume_id,
        "candidate_id": cand["id"],
        "professional_summary": f"{cand['name']} is a seasoned {cand['role']} with {cand['exp']} years of progressive experience. {cand['education']}. Known for {cand['achievements'][0].lower()} and other high-impact contributions.",
        "key_stats": {
            "years_experience": cand["exp"],
            "certifications": cand["certs"],
            "top_skills_count": len(cand["skills"]),
            "industries": ["Technology", "Finance"] if cand["exp"] > 7 else ["Technology"],
            "projects_led": max(1, cand["exp"] // 2),
            "team_size_managed": max(0, (cand["exp"] - 3) * 3) if cand["exp"] > 3 else 0,
        },
        "strong_points": [
            f"{cand['exp']}+ years in {cand['role']} roles",
            f"Expert in {', '.join(cand['skills'][:3])}",
            cand["achievements"][0],
            f"{cand['certs']} professional certifications",
            cand["education"],
        ],
        "career_trajectory": [
            {"period": f"{2026 - cand['exp']}-{2026 - max(0, cand['exp']-3)}", "role": f"Junior {cand['role'].split()[-1]}", "company": "StartupCo", "highlight": "Built foundational skills"},
            {"period": f"{2026 - max(0, cand['exp']-3)}-{2026 - max(0, cand['exp']-6)}", "role": cand["role"], "company": "MidCorp", "highlight": cand["achievements"][1] if len(cand["achievements"]) > 1 else "Key contributor"},
            {"period": f"{2026 - max(0, cand['exp']-6)}-Present", "role": f"Senior {cand['role']}", "company": "Enterprise Inc", "highlight": cand["achievements"][0]},
        ][:min(3, max(1, cand["exp"] // 3))],
        "top_skills": [
            {"skill": s, "proficiency": "Expert" if i < 2 else "Advanced" if i < 4 else "Intermediate", "years": max(1, cand["exp"] - i * 2)}
            for i, s in enumerate(cand["skills"])
        ],
        "notable_achievements": cand["achievements"],
        "condensed_html": None,
        "condensed_pdf_url": f"/api/v1/resume-processing/condensed/{resume_id}/pdf",
        "original_page_count": orig_pages,
        "condensed_page_count": 3,
        "compression_ratio": round(3 / orig_pages, 2) if orig_pages > 3 else 1.0,
        "condensation_quality": 0.92,
        "generated_at": datetime.now().isoformat(),
    }


def _mock_highlights_card(cand: dict, resume_id: int, views: int = 0, downloads: int = 0) -> dict:
    return {
        "resume_id": resume_id,
        "candidate_id": cand["id"],
        "candidate_name": cand["name"],
        "thumbnail_url": f"/api/v1/resume-processing/thumbnail/{resume_id}/image",
        "preview_text": f"{cand['role']} with {cand['exp']} years experience. {cand['education']}.",
        "professional_summary": f"Experienced {cand['role']} specializing in {', '.join(cand['skills'][:3])}. {cand['achievements'][0]}.",
        "years_experience": cand["exp"],
        "top_skills": cand["skills"][:5],
        "strong_points": [cand['achievements'][0], f"{cand['certs']} certifications", f"Expert in {cand['skills'][0]}"],
        "education_highlight": cand["education"],
        "certifications_count": cand["certs"],
        "original_format": "docx" if cand["id"] % 3 == 0 else "pdf",
        "page_count": max(1, cand["exp"] // 3),
        "has_condensed": cand["exp"] > 4,
        "last_updated": (datetime.now() - timedelta(days=cand["id"] * 3)).isoformat(),
        "view_count": views,
        "download_count": downloads,
    }


# ═══════════════════════════════════════════════════════════════════════════
# 1. THUMBNAIL / PREVIEW ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/thumbnails",
    response_model=ThumbnailBatchResponse,
    summary="Get all resume thumbnails",
)
async def get_all_thumbnails(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    organization_id: Optional[int] = Query(None),
):
    """Get paginated list of resume preview thumbnails."""
    thumbnails = [
        _mock_thumbnail(c, c["id"]) for c in SAMPLE_CANDIDATES
    ]
    start = (page - 1) * per_page
    return {
        "thumbnails": thumbnails[start:start + per_page],
        "total": len(thumbnails),
        "generated": len(thumbnails),
        "failed": 0,
    }


@router.get(
    "/thumbnail/{resume_id}",
    response_model=ThumbnailResponse,
    summary="Get resume thumbnail",
)
async def get_thumbnail(resume_id: int):
    """Get preview thumbnail for a specific resume."""
    cand = next((c for c in SAMPLE_CANDIDATES if c["id"] == resume_id), None)
    if not cand:
        raise HTTPException(status_code=404, detail="Resume not found")
    return _mock_thumbnail(cand, resume_id)


@router.post(
    "/thumbnail/{resume_id}/generate",
    response_model=ThumbnailResponse,
    status_code=201,
    summary="Generate resume thumbnail",
)
async def generate_thumbnail(resume_id: int, background_tasks: BackgroundTasks):
    """Generate a preview thumbnail from the first page of a resume."""
    cand = next((c for c in SAMPLE_CANDIDATES if c["id"] == resume_id), SAMPLE_CANDIDATES[0])
    return _mock_thumbnail(cand, resume_id)


@router.post(
    "/thumbnails/batch-generate",
    response_model=ThumbnailBatchResponse,
    summary="Batch generate thumbnails",
)
async def batch_generate_thumbnails(
    resume_ids: List[int] = Query(None, description="Specific resume IDs, or all if omitted"),
    background_tasks: BackgroundTasks = None,
):
    """Generate thumbnails for multiple resumes in batch."""
    targets = SAMPLE_CANDIDATES if not resume_ids else [c for c in SAMPLE_CANDIDATES if c["id"] in resume_ids]
    thumbnails = [_mock_thumbnail(c, c["id"]) for c in targets]
    return {
        "thumbnails": thumbnails,
        "total": len(targets),
        "generated": len(thumbnails),
        "failed": 0,
    }


@router.get(
    "/thumbnail/{resume_id}/image",
    summary="Serve thumbnail image",
)
async def serve_thumbnail_image(resume_id: int):
    """Serve the actual thumbnail image file (placeholder SVG)."""
    cand = next((c for c in SAMPLE_CANDIDATES if c["id"] == resume_id), SAMPLE_CANDIDATES[0])
    # Return SVG placeholder representing a resume preview
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="280" viewBox="0 0 200 280">
      <rect width="200" height="280" fill="#f8fafc" stroke="#e2e8f0" stroke-width="2" rx="4"/>
      <rect x="15" y="15" width="170" height="4" fill="#1e293b" rx="2"/>
      <text x="15" y="35" font-family="system-ui" font-size="8" fill="#1e293b" font-weight="bold">{cand['name']}</text>
      <text x="15" y="46" font-family="system-ui" font-size="6" fill="#64748b">{cand['role']}</text>
      <line x1="15" y1="55" x2="185" y2="55" stroke="#e2e8f0" stroke-width="1"/>
      <text x="15" y="68" font-family="system-ui" font-size="6" fill="#475569">Skills: {', '.join(cand['skills'][:3])}</text>
      <text x="15" y="80" font-family="system-ui" font-size="6" fill="#475569">{cand['education'][:40]}</text>
      <rect x="15" y="92" width="170" height="3" fill="#e2e8f0" rx="1"/>
      <rect x="15" y="100" width="150" height="3" fill="#e2e8f0" rx="1"/>
      <rect x="15" y="108" width="160" height="3" fill="#e2e8f0" rx="1"/>
      <rect x="15" y="116" width="140" height="3" fill="#e2e8f0" rx="1"/>
      <rect x="15" y="128" width="170" height="3" fill="#e2e8f0" rx="1"/>
      <rect x="15" y="136" width="155" height="3" fill="#e2e8f0" rx="1"/>
      <rect x="15" y="144" width="165" height="3" fill="#e2e8f0" rx="1"/>
    </svg>"""
    from fastapi.responses import Response
    return Response(content=svg, media_type="image/svg+xml")


# ═══════════════════════════════════════════════════════════════════════════
# 2. DOCX-TO-PDF CONVERSION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post(
    "/convert/{resume_id}",
    response_model=ConversionResponse,
    status_code=201,
    summary="Convert resume to PDF",
)
async def convert_to_pdf(
    resume_id: int,
    background_tasks: BackgroundTasks,
):
    """Convert a DOCX/DOC resume to PDF for consistent storage and viewing."""
    cand = next((c for c in SAMPLE_CANDIDATES if c["id"] == resume_id), SAMPLE_CANDIDATES[0])
    orig_fmt = "docx" if resume_id % 3 == 0 else "doc" if resume_id % 5 == 0 else "pdf"
    orig_size = 85000 + resume_id * 12000
    conv_size = int(orig_size * 0.75)
    return {
        "resume_id": resume_id,
        "original_format": orig_fmt,
        "converted_format": "pdf",
        "original_size": orig_size,
        "converted_size": conv_size if orig_fmt != "pdf" else orig_size,
        "conversion_status": "completed" if orig_fmt != "pdf" else "skipped",
        "converted_path": f"/storage/resumes/{resume_id}/resume.pdf",
        "converted_at": datetime.now().isoformat(),
    }


@router.post(
    "/convert/batch",
    response_model=ConversionBatchResponse,
    summary="Batch convert resumes to PDF",
)
async def batch_convert_to_pdf(
    resume_ids: Optional[List[int]] = Query(None),
    convert_all_pending: bool = Query(False),
    background_tasks: BackgroundTasks = None,
):
    """Batch convert all non-PDF resumes to PDF format."""
    targets = SAMPLE_CANDIDATES if not resume_ids else [c for c in SAMPLE_CANDIDATES if c["id"] in resume_ids]
    conversions = []
    completed = 0
    for c in targets:
        orig_fmt = "docx" if c["id"] % 3 == 0 else "doc" if c["id"] % 5 == 0 else "pdf"
        is_conv = orig_fmt != "pdf"
        orig_size = 85000 + c["id"] * 12000
        conversions.append({
            "resume_id": c["id"],
            "original_format": orig_fmt,
            "converted_format": "pdf",
            "original_size": orig_size,
            "converted_size": int(orig_size * 0.75) if is_conv else orig_size,
            "conversion_status": "completed" if is_conv else "skipped",
            "converted_path": f"/storage/resumes/{c['id']}/resume.pdf",
            "converted_at": datetime.now().isoformat(),
        })
        if is_conv:
            completed += 1
    return {
        "conversions": conversions,
        "total": len(targets),
        "completed": completed,
        "failed": 0,
    }


@router.get(
    "/convert/{resume_id}/status",
    response_model=ConversionResponse,
    summary="Get conversion status",
)
async def get_conversion_status(resume_id: int):
    """Check conversion status for a specific resume."""
    orig_fmt = "docx" if resume_id % 3 == 0 else "pdf"
    orig_size = 85000 + resume_id * 12000
    return {
        "resume_id": resume_id,
        "original_format": orig_fmt,
        "converted_format": "pdf",
        "original_size": orig_size,
        "converted_size": int(orig_size * 0.75),
        "conversion_status": "completed",
        "converted_path": f"/storage/resumes/{resume_id}/resume.pdf",
        "converted_at": datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════
# 3. DOWNLOAD / VIEW TRACKING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

_download_logs: List[Dict[str, Any]] = []


@router.post(
    "/track",
    response_model=DownloadLogResponse,
    status_code=201,
    summary="Track resume view/download",
)
async def track_access(request: DownloadTrackRequest):
    """Log when a recruiter views or downloads a candidate resume."""
    log_entry = {
        "id": len(_download_logs) + 1,
        "resume_id": request.resume_id,
        "candidate_id": request.candidate_id,
        "recruiter_id": request.recruiter_id,
        "recruiter_name": request.recruiter_name,
        "action": request.action,
        "source_page": request.source_page,
        "accessed_at": datetime.now().isoformat(),
    }
    _download_logs.append(log_entry)
    return log_entry


@router.get(
    "/track/resume/{resume_id}",
    response_model=DownloadAnalytics,
    summary="Get resume access analytics",
)
async def get_resume_analytics(
    resume_id: int,
    days: int = Query(30, ge=1, le=365),
):
    """Get detailed analytics for a specific resume's views and downloads."""
    cand = next((c for c in SAMPLE_CANDIDATES if c["id"] == resume_id), SAMPLE_CANDIDATES[0])
    # Generate mock history
    history = []
    for i in range(15):
        rec = RECRUITERS[i % len(RECRUITERS)]
        action = ["view", "view", "view", "download", "preview"][i % 5]
        history.append({
            "id": i + 1,
            "resume_id": resume_id,
            "candidate_id": cand["id"],
            "recruiter_id": rec["id"],
            "recruiter_name": rec["name"],
            "action": action,
            "source_page": ["ats_workflow", "candidate_crm", "search", "aggregate_reports"][i % 4],
            "accessed_at": (datetime.now() - timedelta(hours=i * 8)).isoformat(),
        })
    views = sum(1 for h in history if h["action"] == "view")
    downloads = sum(1 for h in history if h["action"] == "download")
    previews = sum(1 for h in history if h["action"] == "preview")
    return {
        "resume_id": resume_id,
        "candidate_id": cand["id"],
        "candidate_name": cand["name"],
        "total_views": views,
        "total_downloads": downloads,
        "total_previews": previews,
        "total_prints": 0,
        "unique_recruiters": len(set(h["recruiter_id"] for h in history)),
        "last_accessed": history[0]["accessed_at"] if history else None,
        "access_history": history[:10],
        "access_by_source": {"ats_workflow": 5, "candidate_crm": 4, "search": 3, "aggregate_reports": 3},
        "daily_trend": [
            {"date": (datetime.now() - timedelta(days=d)).strftime("%Y-%m-%d"), "views": 3 + d % 4, "downloads": 1 + d % 2}
            for d in range(min(days, 14))
        ],
    }


@router.get(
    "/track/recruiter/{recruiter_id}",
    response_model=RecruiterAccessReport,
    summary="Get recruiter access report",
)
async def get_recruiter_access(
    recruiter_id: int,
    days: int = Query(30, ge=1, le=365),
):
    """Get report of all resume access activity by a specific recruiter."""
    rec = next((r for r in RECRUITERS if r["id"] == recruiter_id), RECRUITERS[0])
    accesses = []
    for i, cand in enumerate(SAMPLE_CANDIDATES[:5]):
        accesses.append({
            "id": i + 1,
            "resume_id": cand["id"],
            "candidate_id": cand["id"],
            "recruiter_id": recruiter_id,
            "recruiter_name": rec["name"],
            "action": "view" if i % 3 != 0 else "download",
            "source_page": "ats_workflow",
            "accessed_at": (datetime.now() - timedelta(hours=i * 12)).isoformat(),
        })
    return {
        "recruiter_id": recruiter_id,
        "recruiter_name": rec["name"],
        "recruiter_email": rec["email"],
        "total_views": sum(1 for a in accesses if a["action"] == "view"),
        "total_downloads": sum(1 for a in accesses if a["action"] == "download"),
        "resumes_accessed": len(accesses),
        "last_activity": accesses[0]["accessed_at"] if accesses else None,
        "recent_accesses": accesses,
    }


@router.get(
    "/track/top-viewed",
    summary="Get most viewed resumes",
)
async def get_top_viewed(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
):
    """Get the most viewed/downloaded resumes for the given period."""
    results = []
    for i, cand in enumerate(sorted(SAMPLE_CANDIDATES, key=lambda c: c["exp"], reverse=True)[:limit]):
        results.append({
            "resume_id": cand["id"],
            "candidate_id": cand["id"],
            "candidate_name": cand["name"],
            "role": cand["role"],
            "total_views": 25 - i * 3,
            "total_downloads": 8 - i,
            "unique_recruiters": 5 - i // 2,
            "last_accessed": (datetime.now() - timedelta(hours=i * 6)).isoformat(),
        })
    return results


# ═══════════════════════════════════════════════════════════════════════════
# 4. AI RESUME CONDENSATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post(
    "/condense/{resume_id}",
    response_model=CondensedResumeResponse,
    status_code=201,
    summary="Condense resume to 3 pages",
)
async def condense_resume(
    resume_id: int,
    target_pages: int = Query(3, ge=1, le=5),
    focus_areas: Optional[List[str]] = Query(None),
    job_context: Optional[str] = Query(None),
    background_tasks: BackgroundTasks = None,
):
    """
    AI-powered resume condensation.

    Takes any format/length resume and condenses it to a specified page count (default 3),
    preserving the best stats, strong points, and experience highlights.
    """
    cand = next((c for c in SAMPLE_CANDIDATES if c["id"] == resume_id), SAMPLE_CANDIDATES[0])
    return _mock_condensed(cand, resume_id)


@router.get(
    "/condensed/{resume_id}",
    response_model=CondensedResumeResponse,
    summary="Get condensed resume",
)
async def get_condensed_resume(resume_id: int):
    """Get the previously condensed version of a resume."""
    cand = next((c for c in SAMPLE_CANDIDATES if c["id"] == resume_id), SAMPLE_CANDIDATES[0])
    return _mock_condensed(cand, resume_id)


@router.post(
    "/condense/batch",
    summary="Batch condense resumes",
)
async def batch_condense(
    resume_ids: Optional[List[int]] = Query(None),
    target_pages: int = Query(3, ge=1, le=5),
    background_tasks: BackgroundTasks = None,
):
    """Batch condense multiple resumes to target page count."""
    job_id = str(uuid4())[:8]
    targets = SAMPLE_CANDIDATES if not resume_ids else [c for c in SAMPLE_CANDIDATES if c["id"] in resume_ids]
    return {
        "job_id": f"condense_{job_id}",
        "status": "processing",
        "total": len(targets),
        "completed": 0,
        "target_pages": target_pages,
        "estimated_time_seconds": len(targets) * 15,
        "message": f"Condensing {len(targets)} resumes to {target_pages} pages each",
    }


@router.get(
    "/condensed/{resume_id}/pdf",
    summary="Download condensed resume PDF",
)
async def download_condensed_pdf(resume_id: int):
    """Download the condensed resume as a PDF file."""
    return {
        "resume_id": resume_id,
        "download_url": f"/storage/resumes/{resume_id}/condensed_3page.pdf",
        "file_name": f"condensed_resume_{resume_id}.pdf",
        "file_size": 45000 + resume_id * 5000,
        "message": "PDF download ready",
    }


# ═══════════════════════════════════════════════════════════════════════════
# 5. HIGHLIGHTS CARDS FOR APPLICANT VIEWS
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/highlights",
    response_model=List[ResumeHighlightsCard],
    summary="Get resume highlights cards for applicant view",
)
async def get_highlights_cards(
    candidate_ids: Optional[List[int]] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    organization_id: Optional[int] = Query(None),
):
    """
    Get resume highlight cards with thumbnails for applicant cards.

    Returns compact resume summaries with preview thumbnails, key stats,
    strong points, and access counts — ideal for recruiter pipeline views.
    """
    targets = SAMPLE_CANDIDATES if not candidate_ids else [c for c in SAMPLE_CANDIDATES if c["id"] in candidate_ids]
    cards = []
    for c in targets:
        views = 20 - c["id"] * 2
        downloads = max(1, views // 3)
        cards.append(_mock_highlights_card(c, c["id"], views, downloads))
    start = (page - 1) * per_page
    return cards[start:start + per_page]


@router.get(
    "/highlights/{candidate_id}",
    response_model=ResumeHighlightsCard,
    summary="Get resume highlights for a candidate",
)
async def get_candidate_highlights(candidate_id: int):
    """Get resume highlights card for a specific candidate."""
    cand = next((c for c in SAMPLE_CANDIDATES if c["id"] == candidate_id), None)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return _mock_highlights_card(cand, candidate_id, views=12, downloads=4)


# ═══════════════════════════════════════════════════════════════════════════
# 6. PROCESSING STATS / OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/stats",
    response_model=ResumeProcessingStats,
    summary="Get resume processing statistics",
)
async def get_processing_stats(
    organization_id: Optional[int] = Query(None),
):
    """Get overall resume processing statistics and analytics."""
    return {
        "total_resumes": 847,
        "total_parsed": 812,
        "total_converted": 234,
        "total_condensed": 156,
        "total_thumbnails": 812,
        "total_views": 3420,
        "total_downloads": 987,
        "format_breakdown": {"pdf": 613, "docx": 198, "doc": 36},
        "avg_page_count": 4.2,
        "avg_condensation_ratio": 0.38,
        "top_viewed_resumes": [
            {"candidate_name": c["name"], "views": 30 - i * 4, "downloads": 10 - i}
            for i, c in enumerate(SAMPLE_CANDIDATES[:5])
        ],
        "top_downloading_recruiters": [
            {"recruiter_name": r["name"], "downloads": 45 - i * 8}
            for i, r in enumerate(RECRUITERS[:5])
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# 7. AUTO-PROCESS ON UPLOAD (WEBHOOK-STYLE)
# ═══════════════════════════════════════════════════════════════════════════

@router.post(
    "/auto-process/{resume_id}",
    summary="Auto-process resume after upload",
)
async def auto_process_resume(
    resume_id: int,
    convert_to_pdf: bool = Query(True),
    generate_thumbnail: bool = Query(True),
    condense: bool = Query(True),
    target_pages: int = Query(3, ge=1, le=5),
    background_tasks: BackgroundTasks = None,
):
    """
    Automatically process a newly uploaded resume:
    1. Convert DOCX/DOC to PDF
    2. Generate preview thumbnail
    3. Condense to target pages
    4. Extract highlights for applicant cards

    This endpoint is designed to be called as a post-upload webhook.
    """
    job_id = str(uuid4())[:8]
    steps = []
    if convert_to_pdf:
        steps.append({"step": "convert_to_pdf", "status": "completed", "duration_ms": 1200})
    if generate_thumbnail:
        steps.append({"step": "generate_thumbnail", "status": "completed", "duration_ms": 800})
    if condense:
        steps.append({"step": "condense_resume", "status": "completed", "duration_ms": 5400, "target_pages": target_pages})
    steps.append({"step": "extract_highlights", "status": "completed", "duration_ms": 300})

    return {
        "job_id": f"autoprocess_{job_id}",
        "resume_id": resume_id,
        "status": "completed",
        "steps": steps,
        "total_duration_ms": sum(s["duration_ms"] for s in steps),
        "message": f"Resume {resume_id} fully processed: {len(steps)} steps completed",
    }
