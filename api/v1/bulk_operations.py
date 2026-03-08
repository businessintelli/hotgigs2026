"""Comprehensive bulk operations API with background job tracking and notifications."""

import logging
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
import string

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.bulk_operations import (
    ImportBatchResult, ParsingResult, ExcelImportResult,
    PlacementImportResult, RequirementImportResult,
    BatchScoreResult, ScoredCandidate,
    SkillExtractionResult, ExtractedSkill, BatchSkillExtractionResult,
    BatchPlacementPredictionResult, PlacementPrediction,
    MarketAnalysisResult, SkillMarketData,
    BulkAnalysisDashboard, SkillDemandEntry,
    ExportResult, ImportHistoryEntry, TemplateInfo, ColumnDefinition,
    JobCreateResponse, ImportJobResponse, ImportJobListResponse,
    FailureRecord, FailureDownloadResponse, RetryResponse,
    JobCompletionNotification,
)
from models.import_job import ImportJob, ImportJobStatus, ImportJobType
from services.import_job_service import ImportJobService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bulk", tags=["Bulk Operations"])


# ────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ────────────────────────────────────────────────────────────────────────────

def _generate_batch_id() -> str:
    """Generate unique batch ID."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"BATCH-{timestamp}-{random_suffix}"


def _extract_from_filename(filename: str) -> tuple:
    """Extract candidate info from filename pattern."""
    name_email = filename.replace(".pdf", "").replace(".docx", "").replace(".doc", "")
    parts = name_email.split("_")

    first_name = parts[0] if len(parts) > 0 else "Unknown"
    last_name = parts[1] if len(parts) > 1 else "Candidate"
    email = parts[2] if len(parts) > 2 else f"{first_name.lower()}.{last_name.lower()}@example.com"
    skills = parts[3:] if len(parts) > 3 else []

    return first_name, last_name, email, skills


async def _simulate_background_processing(job: ImportJob, db: Optional[AsyncSession]):
    """Simulate background processing of an import job."""
    try:
        # Simulate processing delay
        await asyncio.sleep(0.5)

        # Generate mock results
        success_records = []
        failure_records = []
        skipped_records = []

        for i in range(job.total_records):
            # Mock: 80% success, 10% failure, 10% skipped
            rand = random.random()

            if rand < 0.80:
                success_records.append({
                    "row_number": i + 1,
                    "data_summary": {"email": f"user{i}@example.com", "name": f"User {i}"},
                    "created_id": 1000 + i,
                })
            elif rand < 0.90:
                failure_records.append({
                    "row_number": i + 1,
                    "data": {"email": f"invalid{i}", "name": f"User {i}"},
                    "errors": ["Email is invalid", "Skills field is empty"],
                    "field_errors": {"email": "Invalid email format", "skills": "Required field"},
                })
            else:
                skipped_records.append({
                    "row_number": i + 1,
                    "data": {"email": f"dup{i}@example.com"},
                    "reason": "Duplicate email already exists",
                })

            # Update progress
            await ImportJobService.update_progress(
                db, job.id,
                processed=i + 1,
                success=len(success_records),
                failure=len(failure_records),
                skipped=len(skipped_records),
            )
            await asyncio.sleep(0.01)  # Small delay between updates

        # Complete the job
        await ImportJobService.complete_job(
            db, job.id,
            success_records=success_records,
            failure_records=failure_records,
            skipped_records=skipped_records,
        )

        # Create completion notification
        await ImportJobService.create_completion_notification(db, job)

    except Exception as e:
        logger.error(f"Error processing job {job.id}: {str(e)}")
        await ImportJobService.fail_job(db, job.id, str(e))


# ────────────────────────────────────────────────────────────────────────────
# BULK RESUME IMPORT ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────

@router.post(
    "/resumes/upload",
    response_model=JobCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Bulk resume upload (background job)",
    description="Upload multiple resume files (up to 50) for batch processing.",
)
async def bulk_upload_resumes(
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_db),
) -> JobCreateResponse:
    """
    Bulk upload multiple resume files.
    Returns immediately with job_id; processing happens in background.

    Args:
        files: List of resume files (max 50)
        session: Database session

    Returns:
        JobCreateResponse with job_id and status URL
    """
    try:
        if len(files) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 files allowed per batch",
            )

        # Create job
        job = await ImportJobService.create_job(
            session,
            user_id=1,  # Mock user
            org_id=1,
            job_type=ImportJobType.RESUME_UPLOAD,
            file_name=f"{len(files)}_resumes.zip",
            total_records=len(files),
            job_config={"file_count": len(files)},
        )

        # Start background processing
        asyncio.create_task(_simulate_background_processing(job, session))

        return JobCreateResponse(
            job_id=job.id,
            status="QUEUED",
            status_url=f"/bulk/jobs/{job.id}",
            message="Import job queued. You'll be notified when complete.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resumes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/resumes/from-excel",
    response_model=JobCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import candidates from Excel/CSV (background job)",
    description="Import candidate data from Excel or CSV file.",
)
async def import_resumes_from_excel(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
) -> JobCreateResponse:
    """
    Import candidates from Excel or CSV file (background).
    Expected columns: first_name, last_name, email, phone, skills, experience_years, etc.

    Returns immediately with job_id.
    """
    try:
        # Create job
        job = await ImportJobService.create_job(
            session,
            user_id=1,
            org_id=1,
            job_type=ImportJobType.RESUME_EXCEL,
            file_name=file.filename,
            total_records=15,  # Mock: 15 rows
            job_config={"filename": file.filename},
        )

        # Start background processing
        asyncio.create_task(_simulate_background_processing(job, session))

        return JobCreateResponse(
            job_id=job.id,
            status="QUEUED",
            status_url=f"/bulk/jobs/{job.id}",
            message="Import job queued. You'll be notified when complete.",
        )

    except Exception as e:
        logger.error(f"Error importing from Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ────────────────────────────────────────────────────────────────────────────
# BULK PLACEMENT IMPORT ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────

@router.post(
    "/placements/from-excel",
    response_model=JobCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import placements from Excel (background job)",
    description="Import associate placements/engagement records from Excel.",
)
async def import_placements_from_excel(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
) -> JobCreateResponse:
    """Import placements from Excel file (background)."""
    try:
        job = await ImportJobService.create_job(
            session,
            user_id=1,
            org_id=1,
            job_type=ImportJobType.PLACEMENT_EXCEL,
            file_name=file.filename,
            total_records=10,
            job_config={"filename": file.filename},
        )

        asyncio.create_task(_simulate_background_processing(job, session))

        return JobCreateResponse(
            job_id=job.id,
            status="QUEUED",
            status_url=f"/bulk/jobs/{job.id}",
            message="Import job queued. You'll be notified when complete.",
        )

    except Exception as e:
        logger.error(f"Error importing placements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ────────────────────────────────────────────────────────────────────────────
# BULK REQUIREMENT IMPORT ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────

@router.post(
    "/requirements/from-excel",
    response_model=JobCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import job requirements from Excel (background job)",
    description="Import job requirements/positions from Excel file.",
)
async def import_requirements_from_excel(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
) -> JobCreateResponse:
    """Import job requirements from Excel file (background)."""
    try:
        job = await ImportJobService.create_job(
            session,
            user_id=1,
            org_id=1,
            job_type=ImportJobType.REQUIREMENT_EXCEL,
            file_name=file.filename,
            total_records=6,
            job_config={"filename": file.filename},
        )

        asyncio.create_task(_simulate_background_processing(job, session))

        return JobCreateResponse(
            job_id=job.id,
            status="QUEUED",
            status_url=f"/bulk/jobs/{job.id}",
            message="Import job queued. You'll be notified when complete.",
        )

    except Exception as e:
        logger.error(f"Error importing requirements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ────────────────────────────────────────────────────────────────────────────
# BULK ASSOCIATE IMPORT ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────

@router.post(
    "/associates/from-excel",
    response_model=JobCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import associates from Excel (background job)",
    description="Import associate profiles from Excel file.",
)
async def import_associates_from_excel(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
) -> JobCreateResponse:
    """Import associates from Excel file (background)."""
    try:
        job = await ImportJobService.create_job(
            session,
            user_id=1,
            org_id=1,
            job_type=ImportJobType.ASSOCIATE_EXCEL,
            file_name=file.filename,
            total_records=20,
            job_config={"filename": file.filename},
        )

        asyncio.create_task(_simulate_background_processing(job, session))

        return JobCreateResponse(
            job_id=job.id,
            status="QUEUED",
            status_url=f"/bulk/jobs/{job.id}",
            message="Import job queued. You'll be notified when complete.",
        )

    except Exception as e:
        logger.error(f"Error importing associates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ────────────────────────────────────────────────────────────────────────────
# JOB TRACKING & STATUS ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────

@router.get(
    "/jobs",
    response_model=List[ImportJobListResponse],
    status_code=status.HTTP_200_OK,
    summary="List import jobs",
    description="Get list of import jobs for current user with optional filters.",
)
async def list_import_jobs(
    job_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> List[ImportJobListResponse]:
    """
    List import jobs for current user.

    Args:
        job_type: Filter by job type
        status: Filter by status
        limit: Maximum results (1-100)
        session: Database session

    Returns:
        List of import job summaries
    """
    try:
        jobs = await ImportJobService.list_jobs(
            session,
            user_id=1,
            job_type=job_type,
            status=status,
            limit=limit,
        )

        return [
            ImportJobListResponse(
                id=job.id,
                job_type=job.job_type,
                status=job.status,
                total_records=job.total_records,
                success_count=job.success_count,
                failure_count=job.failure_count,
                skipped_count=job.skipped_count,
                progress_percent=job.progress_percent,
                file_name=job.file_name,
                created_at=job.created_at,
                completed_at=job.completed_at,
            )
            for job in jobs
        ]

    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/jobs/{job_id}",
    response_model=ImportJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get job details",
    description="Get detailed status of a specific import job.",
)
async def get_import_job(
    job_id: int,
    session: AsyncSession = Depends(get_db),
) -> ImportJobResponse:
    """Get detailed job status."""
    try:
        job = await ImportJobService.get_job(session, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        return ImportJobResponse(
            id=job.id,
            user_id=job.user_id,
            organization_id=job.organization_id,
            job_type=job.job_type,
            status=job.status,
            total_records=job.total_records,
            processed_records=job.processed_records,
            success_count=job.success_count,
            failure_count=job.failure_count,
            skipped_count=job.skipped_count,
            progress_percent=job.progress_percent,
            file_name=job.file_name,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/jobs/{job_id}/failures",
    response_model=List[FailureRecord],
    status_code=status.HTTP_200_OK,
    summary="Get failure records",
    description="Get list of failed records from a completed job.",
)
async def get_job_failures(
    job_id: int,
    session: AsyncSession = Depends(get_db),
) -> List[FailureRecord]:
    """Get failure records for a job."""
    try:
        job = await ImportJobService.get_job(session, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        failure_data = job.failure_records.get("records", [])
        return [
            FailureRecord(
                row_number=f.get("row_number", 0),
                original_data=f.get("data", {}),
                errors=f.get("errors", []),
                field_errors=f.get("field_errors", {}),
            )
            for f in failure_data
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting failures: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/jobs/{job_id}/failures/download",
    response_model=FailureDownloadResponse,
    status_code=status.HTTP_200_OK,
    summary="Download failure records as Excel",
    description="Generate downloadable Excel file with failure records.",
)
async def download_job_failures(
    job_id: int,
    session: AsyncSession = Depends(get_db),
) -> FailureDownloadResponse:
    """Download failure records as Excel."""
    try:
        job = await ImportJobService.get_job(session, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        failure_excel = await ImportJobService.generate_failure_excel(job)

        return FailureDownloadResponse(
            download_url=f"/bulk/jobs/{job_id}/failures/export.xlsx",
            filename=failure_excel["filename"],
            record_count=failure_excel["record_count"],
            columns=failure_excel["columns"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading failures: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/jobs/{job_id}/successes",
    status_code=status.HTTP_200_OK,
    summary="Get success records",
    description="Get list of successfully imported records.",
)
async def get_job_successes(
    job_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get success records for a job."""
    try:
        job = await ImportJobService.get_job(session, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        return {
            "records": job.success_records.get("records", []),
            "count": job.success_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting successes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/jobs/{job_id}/retry-failures",
    response_model=RetryResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Retry failed records",
    description="Create a new job to re-import only the failed records.",
)
async def retry_job_failures(
    job_id: int,
    session: AsyncSession = Depends(get_db),
) -> RetryResponse:
    """Retry failed records from a previous job."""
    try:
        original_job = await ImportJobService.get_job(session, job_id)
        if not original_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        failure_records = original_job.failure_records.get("records", [])
        if not failure_records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No failures to retry",
            )

        # Create new job with only the failed records
        new_job = await ImportJobService.create_job(
            session,
            user_id=original_job.user_id,
            org_id=original_job.organization_id,
            job_type=original_job.job_type,
            file_name=f"{original_job.file_name}_retry",
            total_records=len(failure_records),
            job_config={"original_job_id": job_id, "retry": True},
        )

        # Start background processing
        asyncio.create_task(_simulate_background_processing(new_job, session))

        return RetryResponse(
            new_job_id=new_job.id,
            original_job_id=job_id,
            records_to_retry=len(failure_records),
            status_url=f"/bulk/jobs/{new_job.id}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying failures: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ────────────────────────────────────────────────────────────────────────────
# BULK AI ANALYSIS ENDPOINTS (Background Jobs)
# ────────────────────────────────────────────────────────────────────────────

@router.post(
    "/ai/batch-score",
    response_model=JobCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Batch AI scoring (background job)",
    description="Score multiple candidates against a requirement using AI.",
)
async def batch_score_candidates(
    requirement_id: int = Query(..., ge=1),
    candidate_ids: List[int] = Query(..., min_items=1, max_items=100),
    session: AsyncSession = Depends(get_db),
) -> JobCreateResponse:
    """Score multiple candidates (background job)."""
    try:
        job = await ImportJobService.create_job(
            session,
            user_id=1,
            org_id=1,
            job_type=ImportJobType.BATCH_SCORE,
            file_name=None,
            total_records=len(candidate_ids),
            job_config={"requirement_id": requirement_id, "candidate_ids": candidate_ids},
        )

        asyncio.create_task(_simulate_background_processing(job, session))

        return JobCreateResponse(
            job_id=job.id,
            status="QUEUED",
            status_url=f"/bulk/jobs/{job.id}",
            message="Batch scoring job queued. Results available when complete.",
        )

    except Exception as e:
        logger.error(f"Error batch scoring: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/ai/skill-extraction",
    response_model=JobCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Batch skill extraction (background job)",
    description="Extract and analyze skills from multiple candidate profiles.",
)
async def batch_extract_skills(
    candidate_ids: List[int] = Query(..., min_items=1, max_items=100),
    session: AsyncSession = Depends(get_db),
) -> JobCreateResponse:
    """Extract skills from multiple candidates (background job)."""
    try:
        job = await ImportJobService.create_job(
            session,
            user_id=1,
            org_id=1,
            job_type=ImportJobType.SKILL_EXTRACTION,
            file_name=None,
            total_records=len(candidate_ids),
            job_config={"candidate_ids": candidate_ids},
        )

        asyncio.create_task(_simulate_background_processing(job, session))

        return JobCreateResponse(
            job_id=job.id,
            status="QUEUED",
            status_url=f"/bulk/jobs/{job.id}",
            message="Skill extraction job queued. Results available when complete.",
        )

    except Exception as e:
        logger.error(f"Error extracting skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/ai/placement-prediction",
    response_model=JobCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Batch placement prediction (background job)",
    description="Predict placement probability for multiple candidates.",
)
async def batch_predict_placements(
    requirement_id: int = Query(..., ge=1),
    candidate_ids: List[int] = Query(..., min_items=1, max_items=100),
    session: AsyncSession = Depends(get_db),
) -> JobCreateResponse:
    """Predict placement probabilities (background job)."""
    try:
        job = await ImportJobService.create_job(
            session,
            user_id=1,
            org_id=1,
            job_type=ImportJobType.PLACEMENT_PREDICTION,
            file_name=None,
            total_records=len(candidate_ids),
            job_config={"requirement_id": requirement_id, "candidate_ids": candidate_ids},
        )

        asyncio.create_task(_simulate_background_processing(job, session))

        return JobCreateResponse(
            job_id=job.id,
            status="QUEUED",
            status_url=f"/bulk/jobs/{job.id}",
            message="Placement prediction job queued. Results available when complete.",
        )

    except Exception as e:
        logger.error(f"Error predicting placements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/ai/market-analysis",
    response_model=MarketAnalysisResult,
    status_code=status.HTTP_200_OK,
    summary="Market analysis for skills (synchronous)",
    description="Analyze market demand and supply for multiple skills.",
)
async def analyze_skill_market(
    skills: List[str] = Query(..., min_items=1, max_items=20),
    session: AsyncSession = Depends(get_db),
) -> MarketAnalysisResult:
    """Analyze market data for skills (fast, synchronous)."""
    try:
        skill_data = [
            SkillMarketData(
                skill=skill,
                demand_level=random.choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"]),
                avg_bill_rate=float(80 + random.randint(0, 100)),
                avg_pay_rate=float(60 + random.randint(0, 80)),
                supply_count=random.randint(10, 500),
                demand_count=random.randint(5, 100),
                competition_index=float(random.randint(30, 95)),
            )
            for skill in skills[:8]
        ]

        highest_demand = max(skill_data, key=lambda x: x.demand_count if x.demand_count else 0)
        lowest_supply = min(skill_data, key=lambda x: x.supply_count)

        return MarketAnalysisResult(
            skills_analyzed=skill_data,
            highest_demand_skill=highest_demand.skill,
            lowest_supply_skill=lowest_supply.skill,
            created_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error analyzing market: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/ai/analysis-dashboard",
    response_model=BulkAnalysisDashboard,
    status_code=status.HTTP_200_OK,
    summary="Bulk AI analysis dashboard",
    description="Comprehensive dashboard with batch scores, skill demand, and insights.",
)
async def get_analysis_dashboard(
    session: AsyncSession = Depends(get_db),
) -> BulkAnalysisDashboard:
    """Get bulk AI analysis dashboard (synchronous)."""
    try:
        recent_batch_scores = [
            BatchScoreResult(
                batch_id=_generate_batch_id(),
                requirement_id=100 + i,
                total_candidates=10 + i,
                scored_candidates=[
                    ScoredCandidate(
                        candidate_id=j,
                        candidate_name=f"Candidate {j}",
                        overall_score=float(70 + random.randint(0, 25)),
                        skill_score=float(75 + random.randint(-5, 10)),
                        experience_score=float(72 + random.randint(-5, 10)),
                        education_score=float(78 + random.randint(-5, 10)),
                        location_score=float(80 + random.randint(-10, 5)),
                        rate_score=float(65 + random.randint(-5, 15)),
                        availability_score=float(85 + random.randint(-5, 10)),
                        culture_score=float(70 + random.randint(-10, 10)),
                    )
                    for j in range(1, 6)
                ],
                avg_score=float(75 + random.randint(-5, 10)),
                score_distribution={"90-100": 2, "80-89": 3, "70-79": 4, "below-70": 1},
                processing_time_ms=random.randint(500, 2000),
                created_at=datetime.utcnow() - timedelta(days=i),
            )
            for i in range(5)
        ]

        top_skills = [
            "Python", "JavaScript", "Java", "TypeScript", "SQL",
            "React", "Docker", "AWS", "C#", "Go",
            "Kubernetes", "Node.js", "PostgreSQL", "Spring Boot", "GraphQL"
        ]

        skill_demand_heatmap = [
            SkillDemandEntry(skill=skill, demand_score=float(50 + random.randint(0, 50)))
            for skill in top_skills
        ]

        return BulkAnalysisDashboard(
            recent_batch_scores=recent_batch_scores,
            total_candidates_scored=342,
            avg_platform_score=74.5,
            skill_demand_heatmap=skill_demand_heatmap,
            placement_success_rate=78.3,
            avg_time_to_fill_days=13.2,
            ai_insights=[
                "Python and JavaScript remain the most in-demand skills with 450+ open positions",
                "Cloud skills (AWS, Docker, Kubernetes) show 35% YoY growth in demand",
                "Full-stack developer positions have 2.3x more candidates than available roles",
                "Kubernetes experience now appearing in 28% of senior engineering requirements",
                "Go and Rust combined show highest salary premiums (+18% vs market average)",
            ],
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ────────────────────────────────────────────────────────────────────────────
# EXPORT ENDPOINTS (Keep as-is, synchronous)
# ────────────────────────────────────────────────────────────────────────────

@router.get(
    "/export/candidates",
    response_model=ExportResult,
    status_code=status.HTTP_200_OK,
    summary="Export candidate database",
    description="Export candidates with optional filters.",
)
async def export_candidates(
    format: str = Query("csv", pattern="^(csv|json)$"),
    status: Optional[str] = Query(None),
    skills: Optional[List[str]] = Query(None),
    location: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    session: AsyncSession = Depends(get_db),
) -> ExportResult:
    """Export candidate database."""
    try:
        export_id = _generate_batch_id()

        return ExportResult(
            export_id=export_id,
            entity_type="candidates",
            format=format,
            filename=f"candidates_export_{datetime.utcnow().strftime('%Y%m%d')}.{format}",
            record_count=150,
            file_size_bytes=45000 if format == "csv" else 52000,
            download_url=f"/api/v1/bulk/exports/{export_id}/download",
            expires_at=datetime.utcnow() + timedelta(days=7),
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error exporting candidates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/export/requirements",
    response_model=ExportResult,
    status_code=status.HTTP_200_OK,
    summary="Export job requirements",
    description="Export job requirements with optional filters.",
)
async def export_requirements(
    format: str = Query("csv", pattern="^(csv|json)$"),
    req_status: Optional[str] = Query(None, alias="status"),
    client: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
) -> ExportResult:
    """Export requirements."""
    try:
        export_id = _generate_batch_id()

        return ExportResult(
            export_id=export_id,
            entity_type="requirements",
            format=format,
            filename=f"requirements_export_{datetime.utcnow().strftime('%Y%m%d')}.{format}",
            record_count=42,
            file_size_bytes=18500 if format == "csv" else 22000,
            download_url=f"/api/v1/bulk/exports/{export_id}/download",
            expires_at=datetime.utcnow() + timedelta(days=7),
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error exporting requirements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/export/placements",
    response_model=ExportResult,
    status_code=status.HTTP_200_OK,
    summary="Export placements/associates",
    description="Export placement records with optional filters.",
)
async def export_placements(
    format: str = Query("csv", pattern="^(csv|json)$"),
    p_status: Optional[str] = Query(None, alias="status"),
    client: Optional[str] = Query(None),
    supplier: Optional[str] = Query(None),
    date_range: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
) -> ExportResult:
    """Export placements."""
    try:
        export_id = _generate_batch_id()

        return ExportResult(
            export_id=export_id,
            entity_type="placements",
            format=format,
            filename=f"placements_export_{datetime.utcnow().strftime('%Y%m%d')}.{format}",
            record_count=78,
            file_size_bytes=35500 if format == "csv" else 42000,
            download_url=f"/api/v1/bulk/exports/{export_id}/download",
            expires_at=datetime.utcnow() + timedelta(days=7),
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error exporting placements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/export/match-results",
    response_model=ExportResult,
    status_code=status.HTTP_200_OK,
    summary="Export match scores",
    description="Export candidate-requirement match scores.",
)
async def export_match_results(
    format: str = Query("csv", pattern="^(csv|json)$"),
    requirement_id: Optional[int] = Query(None),
    min_score: Optional[float] = Query(None),
    session: AsyncSession = Depends(get_db),
) -> ExportResult:
    """Export match results."""
    try:
        export_id = _generate_batch_id()

        return ExportResult(
            export_id=export_id,
            entity_type="match_results",
            format=format,
            filename=f"match_results_export_{datetime.utcnow().strftime('%Y%m%d')}.{format}",
            record_count=35,
            file_size_bytes=12500 if format == "csv" else 15000,
            download_url=f"/api/v1/bulk/exports/{export_id}/download",
            expires_at=datetime.utcnow() + timedelta(days=7),
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error exporting match results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/export/submissions",
    response_model=ExportResult,
    status_code=status.HTTP_200_OK,
    summary="Export submission pipeline data",
    description="Export candidate submissions and pipeline records.",
)
async def export_submissions(
    format: str = Query("csv", pattern="^(csv|json)$"),
    sub_status: Optional[str] = Query(None, alias="status"),
    requirement_id: Optional[int] = Query(None),
    date_range: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
) -> ExportResult:
    """Export submissions."""
    try:
        export_id = _generate_batch_id()

        return ExportResult(
            export_id=export_id,
            entity_type="submissions",
            format=format,
            filename=f"submissions_export_{datetime.utcnow().strftime('%Y%m%d')}.{format}",
            record_count=120,
            file_size_bytes=48500 if format == "csv" else 58000,
            download_url=f"/api/v1/bulk/exports/{export_id}/download",
            expires_at=datetime.utcnow() + timedelta(days=7),
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error exporting submissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ────────────────────────────────────────────────────────────────────────────
# IMPORT TEMPLATES & HISTORY
# ────────────────────────────────────────────────────────────────────────────

@router.get(
    "/templates/{entity_type}",
    response_model=TemplateInfo,
    status_code=status.HTTP_200_OK,
    summary="Download import template",
    description="Get import template with column definitions and sample data.",
)
async def get_import_template(
    entity_type: str,
    session: AsyncSession = Depends(get_db),
) -> TemplateInfo:
    """Get import template for entity type."""
    try:
        templates = {
            "candidates": {
                "columns": [
                    ColumnDefinition(column_name="first_name", required=True, description="Candidate first name", example="John"),
                    ColumnDefinition(column_name="last_name", required=True, description="Candidate last name", example="Doe"),
                    ColumnDefinition(column_name="email", required=True, description="Email address", example="john.doe@example.com"),
                    ColumnDefinition(column_name="phone", required=False, description="Phone number", example="+1-555-0100"),
                    ColumnDefinition(column_name="skills", required=False, description="Comma-separated skills", example="Python,Django,REST API"),
                    ColumnDefinition(column_name="experience_years", required=False, description="Years of experience", example="5.5"),
                    ColumnDefinition(column_name="location", required=False, description="City, State", example="San Francisco, CA"),
                    ColumnDefinition(column_name="current_title", required=False, description="Current job title", example="Senior Python Developer"),
                    ColumnDefinition(column_name="expected_rate", required=False, description="Expected hourly/annual rate", example="95.00"),
                    ColumnDefinition(column_name="source", required=False, description="How candidate was sourced", example="LinkedIn"),
                ],
                "sample_data": [
                    {"first_name": "John", "last_name": "Doe", "email": "john@example.com", "skills": "Python,Django,REST API", "experience_years": 5.5},
                    {"first_name": "Jane", "last_name": "Smith", "email": "jane@example.com", "skills": "JavaScript,React,Node.js", "experience_years": 4.0},
                ],
            },
            "requirements": {
                "columns": [
                    ColumnDefinition(column_name="title", required=True, description="Job title", example="Senior Python Developer"),
                    ColumnDefinition(column_name="department", required=False, description="Department", example="Engineering"),
                    ColumnDefinition(column_name="client_name", required=True, description="Client organization", example="TechCorp Inc"),
                    ColumnDefinition(column_name="skills_required", required=True, description="Comma-separated required skills", example="Python,Django,REST API"),
                    ColumnDefinition(column_name="experience_min", required=False, description="Min years required", example="3"),
                    ColumnDefinition(column_name="experience_max", required=False, description="Max years preferred", example="8"),
                    ColumnDefinition(column_name="location", required=False, description="Location", example="Remote"),
                    ColumnDefinition(column_name="rate_min", required=False, description="Min bill rate", example="85.00"),
                    ColumnDefinition(column_name="rate_max", required=False, description="Max bill rate", example="120.00"),
                    ColumnDefinition(column_name="priority", required=False, description="Priority level", example="high"),
                    ColumnDefinition(column_name="headcount", required=False, description="Number of positions", example="2"),
                ],
                "sample_data": [
                    {"title": "Senior Python Developer", "client_name": "TechCorp Inc", "skills_required": "Python,Django", "experience_min": 3, "rate_min": 85.00},
                ],
            },
            "placements": {
                "columns": [
                    ColumnDefinition(column_name="candidate_email", required=True, description="Candidate email", example="john@example.com"),
                    ColumnDefinition(column_name="requirement_id", required=True, description="Requirement ID", example="101"),
                    ColumnDefinition(column_name="client_name", required=True, description="Client name", example="TechCorp Inc"),
                    ColumnDefinition(column_name="supplier_name", required=False, description="Supplier/Recruiter name", example="StaffPro Solutions"),
                    ColumnDefinition(column_name="bill_rate", required=True, description="Bill rate (hourly)", example="95.00"),
                    ColumnDefinition(column_name="pay_rate", required=True, description="Pay rate (hourly)", example="72.00"),
                    ColumnDefinition(column_name="start_date", required=True, description="Start date", example="2026-04-01"),
                    ColumnDefinition(column_name="end_date", required=False, description="End date", example="2026-06-30"),
                    ColumnDefinition(column_name="status", required=False, description="Status", example="active"),
                ],
                "sample_data": [
                    {"candidate_email": "john@example.com", "requirement_id": 101, "client_name": "TechCorp Inc", "bill_rate": 95.00, "pay_rate": 72.00, "start_date": "2026-04-01"},
                ],
            },
            "associates": {
                "columns": [
                    ColumnDefinition(column_name="candidate_email", required=True, description="Candidate email", example="john@example.com"),
                    ColumnDefinition(column_name="skill_level", required=False, description="Skill level", example="Senior"),
                    ColumnDefinition(column_name="availability", required=False, description="Availability", example="Immediately"),
                    ColumnDefinition(column_name="willing_to_relocate", required=False, description="Willing to relocate", example="No"),
                    ColumnDefinition(column_name="work_authorization", required=False, description="Work authorization", example="US Citizen"),
                ],
                "sample_data": [],
            },
        }

        template = templates.get(entity_type)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template for entity type '{entity_type}' not found",
            )

        return TemplateInfo(
            entity_type=entity_type,
            columns=template["columns"],
            sample_data=template.get("sample_data"),
            download_url=f"/api/v1/bulk/templates/{entity_type}/download",
            created_at=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/import-history",
    response_model=List[ImportHistoryEntry],
    status_code=status.HTTP_200_OK,
    summary="List all import batches",
    description="Get recent import batch history.",
)
async def get_import_history(
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> List[ImportHistoryEntry]:
    """Get recent import history."""
    try:
        history = [
            ImportHistoryEntry(
                batch_id=_generate_batch_id(),
                import_type="resumes",
                total_records=25,
                success_count=24,
                error_count=1,
                imported_by="jane.recruiter@hotgigs.com",
                created_at=datetime.utcnow() - timedelta(hours=i),
            )
            for i in range(5)
        ]

        return history

    except Exception as e:
        logger.error(f"Error getting import history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


logger.info("Bulk Operations router initialized with background job tracking (22 endpoints)")
