import logging
from datetime import datetime, timezone
from typing import Dict, Optional
from app.schemas.job import JobResponse, JobStatus

logger = logging.getLogger("job_service")


class JobManager:
    def __init__(self):
        self._jobs: Dict[str, JobResponse] = {}

    def create_job(self, job_id: str, document_id: str) -> JobResponse:
        now_str = datetime.now(timezone.utc).isoformat()
        job = JobResponse(
            job_id=job_id,
            document_id=document_id,
            status=JobStatus.QUEUED,
            created_at=now_str,
            progress_percentage=0.0,
        )
        self._jobs[job_id] = job
        logger.info(f"Registered job_id={job_id} for document_id={document_id}")
        return job

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: float = 0.0,
        error_msg: Optional[str] = None,
    ) -> Optional[JobResponse]:
        if job_id not in self._jobs:
            return None

        job = self._jobs[job_id]
        job.status = status
        job.progress_percentage = progress
        if error_msg:
            job.error = error_msg

        if status in [JobStatus.DONE, JobStatus.FAILED]:
            job.completed_at = datetime.now(timezone.utc).isoformat()
            if status == JobStatus.DONE:
                job.progress_percentage = 100.0

        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[JobResponse]:
        return self._jobs.get(job_id)


job_manager = JobManager()
