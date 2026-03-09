"""
Resume Processing Schemas — thumbnails, conversion, tracking, condensation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# ═══════════════════════════════════════════════════════════════════════════
# THUMBNAIL SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class ThumbnailResponse(BaseModel):
    resume_id: int
    thumbnail_url: str
    thumbnail_format: str = "png"
    width: int = 200
    height: int = 280
    page_count: int = 1
    preview_text: Optional[str] = None
    generated_at: str


class ThumbnailBatchResponse(BaseModel):
    thumbnails: List[ThumbnailResponse]
    total: int
    generated: int
    failed: int


# ═══════════════════════════════════════════════════════════════════════════
# CONVERSION SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class ConversionRequest(BaseModel):
    resume_id: int
    target_format: str = Field(default="pdf", pattern="^(pdf)$")


class ConversionResponse(BaseModel):
    resume_id: int
    original_format: str
    converted_format: str
    original_size: int
    converted_size: int
    conversion_status: str
    converted_path: str
    converted_at: str


class ConversionBatchResponse(BaseModel):
    conversions: List[ConversionResponse]
    total: int
    completed: int
    failed: int


# ═══════════════════════════════════════════════════════════════════════════
# DOWNLOAD TRACKING SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class DownloadTrackRequest(BaseModel):
    resume_id: int
    candidate_id: int
    recruiter_id: Optional[int] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    action: str = Field(..., pattern="^(view|download|preview|print)$")
    source_page: Optional[str] = None


class DownloadLogResponse(BaseModel):
    id: int
    resume_id: int
    candidate_id: int
    recruiter_id: Optional[int] = None
    recruiter_name: Optional[str] = None
    action: str
    source_page: Optional[str] = None
    accessed_at: str


class DownloadAnalytics(BaseModel):
    resume_id: int
    candidate_id: int
    candidate_name: Optional[str] = None
    total_views: int = 0
    total_downloads: int = 0
    total_previews: int = 0
    total_prints: int = 0
    unique_recruiters: int = 0
    last_accessed: Optional[str] = None
    access_history: List[DownloadLogResponse] = []
    access_by_source: Dict[str, int] = {}
    daily_trend: List[Dict[str, Any]] = []


class RecruiterAccessReport(BaseModel):
    recruiter_id: int
    recruiter_name: str
    recruiter_email: Optional[str] = None
    total_views: int = 0
    total_downloads: int = 0
    resumes_accessed: int = 0
    last_activity: Optional[str] = None
    recent_accesses: List[DownloadLogResponse] = []


# ═══════════════════════════════════════════════════════════════════════════
# CONDENSED RESUME SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class CondenseRequest(BaseModel):
    resume_id: int
    target_pages: int = Field(default=3, ge=1, le=5)
    focus_areas: Optional[List[str]] = None  # e.g. ["technical_skills", "leadership", "certifications"]
    job_context: Optional[str] = None  # Optional job description for targeted condensation


class CondensedResumeResponse(BaseModel):
    resume_id: int
    candidate_id: int
    professional_summary: str
    key_stats: Dict[str, Any]
    strong_points: List[str]
    career_trajectory: List[Dict[str, Any]]
    top_skills: List[Dict[str, Any]]
    notable_achievements: List[str]
    condensed_html: Optional[str] = None
    condensed_pdf_url: Optional[str] = None
    original_page_count: int
    condensed_page_count: int
    compression_ratio: float
    condensation_quality: float
    generated_at: str


class ResumeHighlightsCard(BaseModel):
    """Compact resume highlights for applicant cards."""
    resume_id: int
    candidate_id: int
    candidate_name: str
    thumbnail_url: Optional[str] = None
    preview_text: Optional[str] = None
    professional_summary: Optional[str] = None
    years_experience: Optional[int] = None
    top_skills: List[str] = []
    strong_points: List[str] = []
    education_highlight: Optional[str] = None
    certifications_count: int = 0
    original_format: str = "pdf"
    page_count: int = 1
    has_condensed: bool = False
    last_updated: Optional[str] = None
    view_count: int = 0
    download_count: int = 0


# ═══════════════════════════════════════════════════════════════════════════
# BATCH / OVERVIEW SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class ResumeProcessingStats(BaseModel):
    total_resumes: int = 0
    total_parsed: int = 0
    total_converted: int = 0
    total_condensed: int = 0
    total_thumbnails: int = 0
    total_views: int = 0
    total_downloads: int = 0
    format_breakdown: Dict[str, int] = {}  # {"pdf": 120, "docx": 45, "doc": 5}
    avg_page_count: float = 0.0
    avg_condensation_ratio: float = 0.0
    top_viewed_resumes: List[Dict[str, Any]] = []
    top_downloading_recruiters: List[Dict[str, Any]] = []
