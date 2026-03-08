"""Service for managing background import jobs and notifications."""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from models.import_job import ImportJob, ImportJobStatus, ImportJobType
from models.enums import NotificationType, NotificationCategory

logger = logging.getLogger(__name__)

# In-memory mock storage for demo purposes (since we don't have a real DB connection in mock mode)
_job_store: Dict[int, ImportJob] = {}
_notification_store: Dict[int, Dict[str, Any]] = {}
_job_id_counter = 1000


class ImportJobService:
    """Service for managing import jobs."""

    @staticmethod
    async def create_job(
        db: Optional[AsyncSession],
        user_id: int,
        org_id: Optional[int],
        job_type: str,
        file_name: Optional[str],
        total_records: int,
        job_config: Dict[str, Any],
    ) -> ImportJob:
        """Create a new import job."""
        global _job_id_counter

        job = ImportJob(
            id=_job_id_counter,
            user_id=user_id,
            organization_id=org_id,
            job_type=job_type,
            status=ImportJobStatus.QUEUED,
            total_records=total_records,
            processed_records=0,
            success_count=0,
            failure_count=0,
            skipped_count=0,
            progress_percent=0.0,
            success_records={},
            failure_records={},
            skipped_records={},
            job_config=job_config,
            file_name=file_name,
            started_at=None,
            completed_at=None,
            error_message=None,
            notification_sent=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
        )

        _job_store[_job_id_counter] = job
        _job_id_counter += 1

        logger.info(f"Created import job {job.id} of type {job_type} for user {user_id}")
        return job

    @staticmethod
    async def update_progress(
        db: Optional[AsyncSession],
        job_id: int,
        processed: int,
        success: int,
        failure: int,
        skipped: int,
    ) -> ImportJob:
        """Update job progress."""
        job = _job_store.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.processed_records = processed
        job.success_count = success
        job.failure_count = failure
        job.skipped_count = skipped

        if job.total_records > 0:
            job.progress_percent = (processed / job.total_records) * 100

        if job.status == ImportJobStatus.QUEUED:
            job.status = ImportJobStatus.PROCESSING
            job.started_at = datetime.utcnow()

        job.updated_at = datetime.utcnow()
        _job_store[job_id] = job

        logger.info(f"Updated job {job_id}: {processed}/{job.total_records} processed")
        return job

    @staticmethod
    async def complete_job(
        db: Optional[AsyncSession],
        job_id: int,
        success_records: List[Dict[str, Any]],
        failure_records: List[Dict[str, Any]],
        skipped_records: List[Dict[str, Any]],
    ) -> ImportJob:
        """Mark job as completed."""
        job = _job_store.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.success_records = {"records": success_records, "count": len(success_records)}
        job.failure_records = {"records": failure_records, "count": len(failure_records)}
        job.skipped_records = {"records": skipped_records, "count": len(skipped_records)}
        job.completed_at = datetime.utcnow()

        if len(failure_records) > 0:
            job.status = ImportJobStatus.COMPLETED_WITH_ERRORS
        else:
            job.status = ImportJobStatus.COMPLETED

        job.progress_percent = 100.0
        job.updated_at = datetime.utcnow()
        _job_store[job_id] = job

        logger.info(
            f"Completed job {job_id}: {job.success_count} success, "
            f"{job.failure_count} failures, {job.skipped_count} skipped"
        )
        return job

    @staticmethod
    async def fail_job(
        db: Optional[AsyncSession],
        job_id: int,
        error_message: str,
    ) -> ImportJob:
        """Mark job as failed."""
        job = _job_store.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = ImportJobStatus.FAILED
        job.error_message = error_message
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        _job_store[job_id] = job

        logger.error(f"Failed job {job_id}: {error_message}")
        return job

    @staticmethod
    async def get_job(
        db: Optional[AsyncSession],
        job_id: int,
    ) -> Optional[ImportJob]:
        """Get a job by ID."""
        return _job_store.get(job_id)

    @staticmethod
    async def list_jobs(
        db: Optional[AsyncSession],
        user_id: int,
        job_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> List[ImportJob]:
        """List jobs for a user with optional filters."""
        jobs = [
            job for job in _job_store.values()
            if job.user_id == user_id
        ]

        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]

        if status:
            jobs = [j for j in jobs if j.status == status]

        # Sort by created_at descending
        jobs.sort(key=lambda x: x.created_at, reverse=True)

        return jobs[:limit]

    @staticmethod
    async def create_completion_notification(
        db: Optional[AsyncSession],
        job: ImportJob,
    ) -> Dict[str, Any]:
        """Create a notification for job completion."""
        if job.failure_count > 0:
            notification_type = NotificationType.WARNING
            message = (
                f"{job.success_count} records imported successfully. "
                f"{job.failure_count} failures. {job.skipped_count} skipped."
            )
        else:
            notification_type = NotificationType.SUCCESS
            message = (
                f"{job.success_count} records imported successfully. "
                f"{job.skipped_count} skipped."
            )

        notification_id = _get_next_notification_id()
        notification = {
            "id": notification_id,
            "user_id": job.user_id,
            "organization_id": job.organization_id,
            "title": f"Import Complete: {job.job_type}",
            "message": message,
            "notification_type": notification_type,
            "category": NotificationCategory.SYSTEM,
            "reference_type": "import_job",
            "reference_id": job.id,
            "is_read": False,
            "action_url": f"/bulk/jobs/{job.id}",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
        }

        job.notification_sent = True
        _notification_store[notification_id] = notification

        return notification

    @staticmethod
    async def generate_failure_excel(job: ImportJob) -> Dict[str, Any]:
        """Generate failure records for Excel download."""
        failure_data = job.failure_records.get("records", [])

        # Build column definitions from first failure record
        columns = ["Row Number", "Errors", "Field Errors"]
        if failure_data and len(failure_data) > 0:
            first_record = failure_data[0]
            if "data" in first_record:
                for key in first_record["data"].keys():
                    columns.append(key)

        rows = []
        for failure in failure_data:
            row = {
                "Row Number": failure.get("row_number", "N/A"),
                "Errors": "; ".join(failure.get("errors", [])),
                "Field Errors": str(failure.get("field_errors", {})),
            }
            # Add original data columns
            if "data" in failure:
                row.update(failure["data"])
            rows.append(row)

        return {
            "filename": f"failures_{job.id}.xlsx",
            "columns": columns,
            "rows": rows,
            "record_count": len(rows),
        }


def _get_next_notification_id() -> int:
    """Get next notification ID."""
    if not _notification_store:
        return 1
    return max(_notification_store.keys()) + 1
