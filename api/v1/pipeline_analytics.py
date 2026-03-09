"""Pipeline Analytics, Email Notifications, Interview Feedback endpoints."""

import logging
import random
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.pipeline_analytics import (
    PipelineFunnel, PhaseConversion, PipelineTrendResponse, PipelineTrend,
    PipelineCompareResponse, PipelineCompare, PhaseBreakdown,
    EmailTemplateResponse, EmailTemplateCreate, EmailLogResponse,
    NotificationHistoryResponse, NotificationStats, NotificationSettingsResponse,
    CandidateNotificationRequest,
    RubricCreate, RubricResponse, RubricCriterion,
    FeedbackSubmit, FeedbackResponse, FeedbackSummary, CalibrateResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pipeline-analytics", tags=["Pipeline Analytics & Notifications"])

# ═══════════════════════════════════════════════════════════════
# SECTION 1: PIPELINE ANALYTICS — CONVERSION RATES & FUNNELS
# ═══════════════════════════════════════════════════════════════

PHASES = ["Applied", "Screening", "Reviewed", "Shortlisted", "Interviewing", "Offered", "Hired"]

MOCK_JOBS = [
    {"id": 1, "title": "Senior Python Developer", "total": 142},
    {"id": 2, "title": "React Frontend Lead", "total": 98},
    {"id": 3, "title": "DevOps Engineer", "total": 76},
    {"id": 4, "title": "Data Scientist", "total": 115},
    {"id": 5, "title": "Product Manager", "total": 89},
]


def _generate_funnel(job: dict) -> PipelineFunnel:
    """Generate realistic funnel data for a job."""
    total = job["total"]
    counts = {}
    remaining = total
    conversion_ranges = [
        (0.55, 0.75), (0.50, 0.70), (0.40, 0.65),
        (0.60, 0.80), (0.70, 0.90), (0.80, 0.95),
    ]
    for i, phase in enumerate(PHASES):
        counts[phase] = remaining
        if i < len(PHASES) - 1:
            rate = random.uniform(*conversion_ranges[i])
            remaining = max(1, int(remaining * rate))

    conversions = []
    for i in range(len(PHASES) - 1):
        from_p, to_p = PHASES[i], PHASES[i + 1]
        entered = counts[from_p]
        converted = counts[to_p]
        rate = round((converted / entered) * 100, 1) if entered else 0
        trends = ["improving", "stable", "declining"]
        conversions.append(PhaseConversion(
            from_phase=from_p, to_phase=to_p,
            candidates_entered=entered, candidates_converted=converted,
            conversion_rate=rate, avg_time_hours=round(random.uniform(12, 120), 1),
            trend=random.choice(trends),
        ))

    worst = min(conversions, key=lambda c: c.conversion_rate)
    overall = round((counts["Hired"] / total) * 100, 1)
    return PipelineFunnel(
        job_id=job["id"], job_title=job["title"],
        phases=PHASES, phase_counts=counts, conversions=conversions,
        total_candidates=total, overall_conversion=overall,
        bottleneck_phase=worst.from_phase,
        bottleneck_reason=f"Only {worst.conversion_rate}% convert from {worst.from_phase} to {worst.to_phase}",
        avg_days_to_hire=round(random.uniform(18, 45), 1),
        generated_at=datetime.utcnow(),
    )


@router.get("/funnel/{job_id}", response_model=PipelineFunnel, summary="Get conversion funnel for a job")
async def get_pipeline_funnel(job_id: int, db: AsyncSession = Depends(get_db)):
    job = next((j for j in MOCK_JOBS if j["id"] == job_id), None)
    if not job:
        job = {"id": job_id, "title": f"Job #{job_id}", "total": random.randint(40, 200)}
    return _generate_funnel(job)


@router.get("/funnels", response_model=List[PipelineFunnel], summary="Get funnels for all active jobs")
async def get_all_funnels(db: AsyncSession = Depends(get_db)):
    return [_generate_funnel(j) for j in MOCK_JOBS]


@router.get("/trends/{job_id}", response_model=PipelineTrendResponse, summary="Historical conversion trends")
async def get_pipeline_trends(
    job_id: int,
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
):
    job = next((j for j in MOCK_JOBS if j["id"] == job_id), None)
    title = job["title"] if job else f"Job #{job_id}"
    trends = []
    base_total = random.randint(40, 150)
    for d in range(days):
        date = (datetime.utcnow() - timedelta(days=days - d)).strftime("%Y-%m-%d")
        total = base_total + random.randint(-5, 8)
        base_total = max(20, total)
        phase_counts = {}
        rem = total
        for i, p in enumerate(PHASES):
            phase_counts[p] = rem
            if i < len(PHASES) - 1:
                rem = max(1, int(rem * random.uniform(0.5, 0.8)))
        conv_rates = {}
        for i in range(len(PHASES) - 1):
            if phase_counts[PHASES[i]] > 0:
                conv_rates[f"{PHASES[i]}→{PHASES[i+1]}"] = round(
                    (phase_counts[PHASES[i + 1]] / phase_counts[PHASES[i]]) * 100, 1
                )
        trends.append(PipelineTrend(
            date=date, phase_counts=phase_counts,
            conversion_rates=conv_rates, total=total,
        ))
    return PipelineTrendResponse(
        job_id=job_id, job_title=title, trends=trends,
        period=f"Last {days} days",
    )


@router.get("/compare", response_model=PipelineCompareResponse, summary="Compare pipelines across jobs")
async def compare_pipelines(
    job_ids: str = Query("1,2,3", description="Comma-separated job IDs"),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(x.strip()) for x in job_ids.split(",")]
    jobs = []
    for jid in ids:
        funnel = await get_pipeline_funnel(jid, db)
        jobs.append(PipelineCompare(
            job_id=jid, job_title=funnel.job_title,
            total=funnel.total_candidates, conversion_rate=funnel.overall_conversion,
            avg_days_to_hire=funnel.avg_days_to_hire, phase_counts=funnel.phase_counts,
        ))
    best = max(jobs, key=lambda j: j.conversion_rate)
    worst_bottle = min(jobs, key=lambda j: j.conversion_rate)
    return PipelineCompareResponse(
        jobs=jobs, best_performing_job=best.job_title,
        worst_bottleneck=f"{worst_bottle.job_title} ({worst_bottle.conversion_rate}%)",
    )


@router.get("/phase-breakdown/{job_id}", response_model=List[PhaseBreakdown], summary="Phase-level breakdown")
async def get_phase_breakdown(job_id: int, db: AsyncSession = Depends(get_db)):
    funnel = await get_pipeline_funnel(job_id, db)
    total = funnel.total_candidates
    sources = ["LinkedIn", "Indeed", "Referral", "Career Page", "Agency"]
    result = []
    for phase in PHASES:
        count = funnel.phase_counts.get(phase, 0)
        result.append(PhaseBreakdown(
            phase=phase, count=count,
            percentage=round((count / total) * 100, 1) if total else 0,
            avg_time_days=round(random.uniform(1, 8), 1),
            top_sources=random.sample(sources, k=min(3, len(sources))),
        ))
    return result


# ═══════════════════════════════════════════════════════════════
# SECTION 2: EMAIL NOTIFICATIONS — CANDIDATE STATUS CHANGE
# ═══════════════════════════════════════════════════════════════

MOCK_TEMPLATES = [
    {"id": 1, "name": "Application Received", "trigger": "applied",
     "subject": "Your application for {job_title} has been received",
     "preview": "Thank you for applying to {job_title} at {company}. We've received your application..."},
    {"id": 2, "name": "Under Review", "trigger": "screening",
     "subject": "Your application is being reviewed — {job_title}",
     "preview": "Good news! Your application for {job_title} is now under review by our team..."},
    {"id": 3, "name": "Shortlisted", "trigger": "shortlisted",
     "subject": "Congratulations! You've been shortlisted for {job_title}",
     "preview": "We're pleased to inform you that you've been shortlisted for the {job_title} position..."},
    {"id": 4, "name": "Interview Scheduled", "trigger": "interviewing",
     "subject": "Interview scheduled for {job_title}",
     "preview": "Your interview for {job_title} has been scheduled. Please find the details below..."},
    {"id": 5, "name": "Offer Extended", "trigger": "offered",
     "subject": "Offer letter for {job_title} at {company}",
     "preview": "We're excited to extend an offer for the {job_title} position. Please review..."},
    {"id": 6, "name": "Not Selected", "trigger": "rejected",
     "subject": "Update on your application for {job_title}",
     "preview": "Thank you for your interest in {job_title}. After careful consideration..."},
]

MOCK_EMAIL_LOGS = []
_candidate_names = ["Alex Chen", "Maya Patel", "James Wilson", "Sofia Rodriguez", "David Kim",
                     "Emma Thompson", "Carlos Rivera", "Priya Sharma", "Tyler Johnson", "Aisha Hassan"]
_notification_types = ["applied", "screening", "shortlisted", "interviewing", "offered", "rejected"]
for i in range(25):
    name = _candidate_names[i % len(_candidate_names)]
    ntype = _notification_types[i % len(_notification_types)]
    sent = datetime.utcnow() - timedelta(hours=random.randint(1, 720))
    MOCK_EMAIL_LOGS.append({
        "id": i + 1,
        "candidate_name": name,
        "candidate_email": f"{name.lower().replace(' ', '.')}@email.com",
        "job_title": random.choice(["Senior Python Dev", "React Lead", "DevOps Engineer", "Data Scientist"]),
        "notification_type": ntype,
        "subject": f"Application update: {ntype.title()}",
        "status": random.choice(["sent", "delivered", "opened", "failed"]),
        "sent_at": sent.isoformat(),
        "delivered_at": (sent + timedelta(seconds=random.randint(5, 300))).isoformat() if random.random() > 0.1 else None,
        "opened_at": (sent + timedelta(hours=random.randint(1, 48))).isoformat() if random.random() > 0.4 else None,
    })


@router.get("/notifications/templates", response_model=List[EmailTemplateResponse], summary="List email templates")
async def list_email_templates(db: AsyncSession = Depends(get_db)):
    return [
        EmailTemplateResponse(
            id=t["id"], name=t["name"], trigger_event=t["trigger"],
            subject_template=t["subject"], body_preview=t["preview"],
            is_active=True, variables={"job_title": "str", "company": "str", "candidate_name": "str"},
        )
        for t in MOCK_TEMPLATES
    ]


@router.post("/notifications/templates", response_model=EmailTemplateResponse, summary="Create email template")
async def create_email_template(data: EmailTemplateCreate, db: AsyncSession = Depends(get_db)):
    new_id = len(MOCK_TEMPLATES) + 1
    return EmailTemplateResponse(
        id=new_id, name=data.name, trigger_event=data.trigger_event,
        subject_template=data.subject_template, body_preview=data.body_text[:100],
        is_active=True, variables=data.variables,
    )


@router.post("/notifications/send", response_model=EmailLogResponse, summary="Send status change notification")
async def send_notification(req: CandidateNotificationRequest, db: AsyncSession = Depends(get_db)):
    name = _candidate_names[req.candidate_id % len(_candidate_names)]
    now = datetime.utcnow()
    return EmailLogResponse(
        id=len(MOCK_EMAIL_LOGS) + 1,
        candidate_name=name,
        candidate_email=f"{name.lower().replace(' ', '.')}@email.com",
        job_title=f"Job #{req.job_id}",
        notification_type=f"status_change_{req.new_status}",
        subject=f"Application Update: Your status has changed to {req.new_status}",
        status="sent", sent_at=now, delivered_at=None, opened_at=None,
    )


@router.get("/notifications/history", response_model=NotificationHistoryResponse, summary="Notification history")
async def get_notification_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(15, ge=5, le=50),
    notification_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    logs = MOCK_EMAIL_LOGS
    if notification_type:
        logs = [l for l in logs if l["notification_type"] == notification_type]
    total_sent = len(logs)
    delivered = sum(1 for l in logs if l["delivered_at"])
    opened = sum(1 for l in logs if l["opened_at"])
    start = (page - 1) * per_page
    page_logs = logs[start:start + per_page]
    return NotificationHistoryResponse(
        total_sent=total_sent, total_delivered=delivered, total_opened=opened,
        delivery_rate=round((delivered / total_sent) * 100, 1) if total_sent else 0,
        open_rate=round((opened / total_sent) * 100, 1) if total_sent else 0,
        logs=[EmailLogResponse(
            id=l["id"], candidate_name=l["candidate_name"], candidate_email=l["candidate_email"],
            job_title=l["job_title"], notification_type=l["notification_type"],
            subject=l["subject"], status=l["status"],
            sent_at=datetime.fromisoformat(l["sent_at"]),
            delivered_at=datetime.fromisoformat(l["delivered_at"]) if l["delivered_at"] else None,
            opened_at=datetime.fromisoformat(l["opened_at"]) if l["opened_at"] else None,
        ) for l in page_logs],
    )


@router.get("/notifications/stats", response_model=NotificationStats, summary="Notification statistics")
async def get_notification_stats(db: AsyncSession = Depends(get_db)):
    by_type = {}
    by_status = {}
    for l in MOCK_EMAIL_LOGS:
        by_type[l["notification_type"]] = by_type.get(l["notification_type"], 0) + 1
        by_status[l["status"]] = by_status.get(l["status"], 0) + 1
    total = len(MOCK_EMAIL_LOGS)
    delivered = by_status.get("delivered", 0) + by_status.get("opened", 0)
    opened = by_status.get("opened", 0)
    return NotificationStats(
        total_sent=total, by_type=by_type, by_status=by_status,
        delivery_rate=round((delivered / total) * 100, 1) if total else 0,
        open_rate=round((opened / total) * 100, 1) if total else 0,
        recent_failures=by_status.get("failed", 0),
    )


@router.get("/notifications/settings", response_model=NotificationSettingsResponse, summary="Get settings")
async def get_notification_settings(db: AsyncSession = Depends(get_db)):
    return NotificationSettingsResponse(
        auto_notify_on_status_change=True,
        enabled_events=["applied", "screening", "shortlisted", "interviewing", "offered", "rejected"],
        candidate_cc_enabled=False, daily_digest=True, templates_count=len(MOCK_TEMPLATES),
    )


# ═══════════════════════════════════════════════════════════════
# SECTION 3: INTERVIEW FEEDBACK FORMS — SCORING RUBRICS
# ═══════════════════════════════════════════════════════════════

MOCK_RUBRICS = [
    {
        "id": 1, "name": "Software Engineer — Technical", "description": "Technical assessment rubric for SWE roles",
        "job_role": "Software Engineer", "stage": "technical",
        "criteria": [
            {"name": "Problem Solving", "description": "Ability to break down complex problems", "weight": 0.25,
             "scale_labels": {1: "Cannot identify problem", 2: "Identifies but struggles", 3: "Adequate approach", 4: "Strong systematic approach", 5: "Exceptional, creative solutions"}},
            {"name": "Code Quality", "description": "Clean, readable, maintainable code", "weight": 0.20,
             "scale_labels": {1: "Messy/unreadable", 2: "Functional but messy", 3: "Acceptable", 4: "Clean and well-organized", 5: "Exemplary coding standards"}},
            {"name": "System Design", "description": "Architecture and scalability thinking", "weight": 0.20,
             "scale_labels": {1: "No design sense", 2: "Basic understanding", 3: "Competent", 4: "Strong architecture skills", 5: "Expert-level design"}},
            {"name": "Communication", "description": "Explains thought process clearly", "weight": 0.15,
             "scale_labels": {1: "Cannot explain", 2: "Unclear explanations", 3: "Adequate", 4: "Clear and articulate", 5: "Exceptional communicator"}},
            {"name": "Culture Fit", "description": "Alignment with team values and collaboration", "weight": 0.20,
             "scale_labels": {1: "Poor fit", 2: "Some concerns", 3: "Neutral", 4: "Good fit", 5: "Excellent cultural alignment"}},
        ],
    },
    {
        "id": 2, "name": "Leadership — Behavioral", "description": "Behavioral interview rubric for leadership roles",
        "job_role": "Manager", "stage": "behavioral",
        "criteria": [
            {"name": "Leadership Style", "description": "Demonstrates effective leadership approach", "weight": 0.25, "scale_labels": {}},
            {"name": "Conflict Resolution", "description": "Handles disagreements constructively", "weight": 0.20, "scale_labels": {}},
            {"name": "Strategic Thinking", "description": "Long-term vision and planning", "weight": 0.20, "scale_labels": {}},
            {"name": "Team Development", "description": "Invests in growing team members", "weight": 0.20, "scale_labels": {}},
            {"name": "Stakeholder Management", "description": "Manages up, down, and across", "weight": 0.15, "scale_labels": {}},
        ],
    },
    {
        "id": 3, "name": "General — First Round", "description": "General-purpose rubric for initial phone screens",
        "job_role": None, "stage": "phone_screen",
        "criteria": [
            {"name": "Relevant Experience", "description": "Years and depth of relevant experience", "weight": 0.30, "scale_labels": {}},
            {"name": "Communication", "description": "Clarity and professionalism", "weight": 0.25, "scale_labels": {}},
            {"name": "Motivation", "description": "Interest in the role and company", "weight": 0.25, "scale_labels": {}},
            {"name": "Availability", "description": "Timeline and logistics fit", "weight": 0.20, "scale_labels": {}},
        ],
    },
]

MOCK_FEEDBACKS = []
_interviewers = [
    {"id": 1, "name": "Sarah Mitchell"}, {"id": 2, "name": "Robert Chen"},
    {"id": 3, "name": "Jennifer Park"}, {"id": 4, "name": "Michael Torres"},
    {"id": 5, "name": "Angela Williams"},
]
for i in range(20):
    interviewer = _interviewers[i % len(_interviewers)]
    rubric = MOCK_RUBRICS[i % len(MOCK_RUBRICS)]
    scores = {c["name"]: random.randint(2, 5) for c in rubric["criteria"]}
    weighted = sum(scores[c["name"]] * c["weight"] for c in rubric["criteria"])
    recs = ["strong_hire", "hire", "neutral", "no_hire"]
    weights = [0.15, 0.35, 0.30, 0.20]
    MOCK_FEEDBACKS.append({
        "id": i + 1, "interview_id": 100 + i, "interviewer_id": interviewer["id"],
        "interviewer_name": interviewer["name"],
        "candidate_id": (i % 8) + 1, "job_id": (i % 5) + 1,
        "interview_stage": rubric["stage"],
        "criteria_scores": scores, "weighted_total": round(weighted, 2),
        "overall_rating": random.randint(2, 5),
        "recommendation": random.choices(recs, weights=weights, k=1)[0],
        "strengths": random.sample(["Strong communicator", "Deep technical skills", "Great culture fit",
                                     "Fast learner", "Leadership potential", "Innovative thinker"], k=random.randint(1, 3)),
        "weaknesses": random.sample(["Limited system design experience", "Could improve communication",
                                      "Needs more leadership examples", "Gap in cloud technologies"], k=random.randint(0, 2)),
        "detailed_notes": f"Candidate showed {random.choice(['strong', 'adequate', 'impressive'])} skills during the interview.",
        "is_submitted": True,
        "submitted_at": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
    })


@router.get("/rubrics", response_model=List[RubricResponse], summary="List scoring rubrics")
async def list_rubrics(
    job_role: Optional[str] = None,
    stage: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    rubrics = MOCK_RUBRICS
    if job_role:
        rubrics = [r for r in rubrics if r.get("job_role") and job_role.lower() in r["job_role"].lower()]
    if stage:
        rubrics = [r for r in rubrics if r["stage"] == stage]
    return [
        RubricResponse(
            id=r["id"], name=r["name"], description=r["description"],
            job_role=r["job_role"], interview_stage=r["stage"],
            criteria=[RubricCriterion(**c) for c in r["criteria"]],
            scale_min=1, scale_max=5, is_active=True, version=1,
        )
        for r in rubrics
    ]


@router.get("/rubrics/{rubric_id}", response_model=RubricResponse, summary="Get rubric detail")
async def get_rubric(rubric_id: int, db: AsyncSession = Depends(get_db)):
    r = next((r for r in MOCK_RUBRICS if r["id"] == rubric_id), None)
    if not r:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return RubricResponse(
        id=r["id"], name=r["name"], description=r["description"],
        job_role=r["job_role"], interview_stage=r["stage"],
        criteria=[RubricCriterion(**c) for c in r["criteria"]],
        scale_min=1, scale_max=5, is_active=True, version=1,
    )


@router.post("/rubrics", response_model=RubricResponse, summary="Create scoring rubric")
async def create_rubric(data: RubricCreate, db: AsyncSession = Depends(get_db)):
    new_id = len(MOCK_RUBRICS) + 1
    return RubricResponse(
        id=new_id, name=data.name, description=data.description,
        job_role=data.job_role, interview_stage=data.interview_stage,
        criteria=data.criteria, scale_min=data.scale_min, scale_max=data.scale_max,
        is_active=True, version=1,
    )


@router.post("/feedback", response_model=FeedbackResponse, summary="Submit interview feedback")
async def submit_feedback(data: FeedbackSubmit, db: AsyncSession = Depends(get_db)):
    # Calculate weighted total if rubric specified
    weighted = None
    if data.rubric_id:
        rubric = next((r for r in MOCK_RUBRICS if r["id"] == data.rubric_id), None)
        if rubric:
            weighted = sum(
                data.criteria_scores.get(c["name"], 3) * c["weight"]
                for c in rubric["criteria"]
            )
            weighted = round(weighted, 2)
    now = datetime.utcnow()
    return FeedbackResponse(
        id=len(MOCK_FEEDBACKS) + 1, interview_id=data.interview_id,
        interviewer_name="Current User", candidate_id=data.candidate_id,
        job_id=data.job_id, interview_stage=data.interview_stage,
        criteria_scores=data.criteria_scores, weighted_total=weighted,
        overall_rating=data.overall_rating, recommendation=data.recommendation,
        strengths=data.strengths, weaknesses=data.weaknesses,
        detailed_notes=data.detailed_notes, is_submitted=True, submitted_at=now,
    )


@router.get("/feedback/candidate/{candidate_id}", response_model=List[FeedbackResponse], summary="Get all feedback for a candidate")
async def get_candidate_feedback(candidate_id: int, db: AsyncSession = Depends(get_db)):
    feedbacks = [f for f in MOCK_FEEDBACKS if f["candidate_id"] == candidate_id]
    return [
        FeedbackResponse(
            id=f["id"], interview_id=f["interview_id"],
            interviewer_name=f["interviewer_name"], candidate_id=f["candidate_id"],
            job_id=f["job_id"], interview_stage=f["interview_stage"],
            criteria_scores=f["criteria_scores"], weighted_total=f["weighted_total"],
            overall_rating=f["overall_rating"], recommendation=f["recommendation"],
            strengths=f["strengths"], weaknesses=f["weaknesses"],
            detailed_notes=f["detailed_notes"], is_submitted=f["is_submitted"],
            submitted_at=datetime.fromisoformat(f["submitted_at"]),
        )
        for f in feedbacks
    ]


@router.get("/feedback/summary/{candidate_id}", response_model=FeedbackSummary, summary="Aggregated feedback summary")
async def get_feedback_summary(candidate_id: int, db: AsyncSession = Depends(get_db)):
    feedbacks = [f for f in MOCK_FEEDBACKS if f["candidate_id"] == candidate_id]
    if not feedbacks:
        raise HTTPException(status_code=404, detail="No feedback found")
    avg_rating = round(sum(f["overall_rating"] for f in feedbacks) / len(feedbacks), 1)
    rec_breakdown = {}
    for f in feedbacks:
        rec_breakdown[f["recommendation"]] = rec_breakdown.get(f["recommendation"], 0) + 1
    # Aggregate criteria averages
    all_criteria = {}
    criteria_counts = {}
    for f in feedbacks:
        for k, v in f["criteria_scores"].items():
            all_criteria[k] = all_criteria.get(k, 0) + v
            criteria_counts[k] = criteria_counts.get(k, 0) + 1
    criteria_avgs = {k: round(all_criteria[k] / criteria_counts[k], 1) for k in all_criteria}
    interviewers = list(set(f["interviewer_name"] for f in feedbacks))
    return FeedbackSummary(
        candidate_id=candidate_id,
        candidate_name=_candidate_names[candidate_id % len(_candidate_names)],
        total_interviews=len(feedbacks), avg_rating=avg_rating,
        recommendation_breakdown=rec_breakdown,
        criteria_averages=criteria_avgs, interviewers=interviewers,
    )


@router.get("/feedback/calibrate", response_model=List[CalibrateResponse], summary="Interviewer calibration report")
async def calibrate_interviewers(db: AsyncSession = Depends(get_db)):
    results = []
    global_avg = sum(f["overall_rating"] for f in MOCK_FEEDBACKS) / len(MOCK_FEEDBACKS)
    for interviewer in _interviewers:
        their_feedbacks = [f for f in MOCK_FEEDBACKS if f["interviewer_id"] == interviewer["id"]]
        if not their_feedbacks:
            continue
        ratings = [f["overall_rating"] for f in their_feedbacks]
        avg = sum(ratings) / len(ratings)
        dist = {}
        for r in ratings:
            dist[r] = dist.get(r, 0) + 1
        harshness = round(avg - global_avg, 2)
        # Consistency = 1 - (std_dev / max_possible_std)
        mean = avg
        variance = sum((r - mean) ** 2 for r in ratings) / len(ratings)
        std_dev = variance ** 0.5
        consistency = round(max(0, 1 - std_dev / 2), 2)
        results.append(CalibrateResponse(
            interviewer_id=interviewer["id"], interviewer_name=interviewer["name"],
            avg_rating=round(avg, 1), total_reviews=len(their_feedbacks),
            rating_distribution=dist, harshness_score=harshness,
            consistency_score=consistency,
        ))
    return results
