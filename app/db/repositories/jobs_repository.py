"""Repository for persisted job lifecycle records."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.contracts.evidence_contract import RESULT_SKIPPED
from app.contracts.job_contract import (
    JOB_STATUS_QUEUED,
    JOB_STATUS_RUNNING,
    JOB_STATUS_STOPPED,
    JobRequest,
    JobResult,
    validate_job_request,
    validate_job_result,
)
from app.db.models import Job


class JobsRepository:
    """Persistence operations for job lifecycle summaries."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_queued_job(
        self,
        target_id: str,
        created_by: str,
        mode: str,
        selected_modules: list[str] | None = None,
        selected_techniques: list[str] | None = None,
        permissions_snapshot: dict[str, object] | None = None,
    ) -> Job:
        """Create a queued job and return the persisted record."""
        request = JobRequest(
            job_id=str(uuid4()),
            target_id=target_id,
            created_by=created_by,
            mode=mode,
            selected_modules=list(selected_modules or []),
            selected_techniques=list(selected_techniques or []),
            permissions_snapshot=dict(permissions_snapshot or {}),
        )
        validate_job_request(request)
        job = Job(
            job_id=request.job_id,
            target_id=request.target_id,
            created_by=request.created_by,
            mode=request.mode,
            selected_modules_json=json.dumps(request.selected_modules),
            selected_techniques_json=json.dumps(request.selected_techniques),
            status=JOB_STATUS_QUEUED,
            result_status=RESULT_SKIPPED,
            evidence_ids_json=json.dumps([]),
            summary="Job queued.",
            error=None,
        )
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def to_job_request(self, job: Job, permissions_snapshot: dict[str, object] | None = None) -> JobRequest:
        """Convert a persisted job into the runner request contract."""
        return JobRequest(
            job_id=job.job_id,
            target_id=job.target_id,
            created_by=job.created_by,
            mode=job.mode,
            selected_modules=json.loads(job.selected_modules_json),
            selected_techniques=json.loads(job.selected_techniques_json),
            permissions_snapshot=dict(permissions_snapshot or {}),
        )

    def complete_job(self, job: Job, result: JobResult) -> Job:
        """Persist the final runner result for a job."""
        validate_job_result(result)
        job.status = result.status
        job.result_status = result.result_status
        job.evidence_ids_json = json.dumps(result.evidence_ids)
        job.summary = result.summary
        job.error = result.error
        job.finished_at = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(job)
        return job

    def mark_running(self, job: Job) -> Job:
        """Persist that a queued job has entered the local in-process runner."""
        job.status = JOB_STATUS_RUNNING
        job.summary = "Job running in local in-process JobRunner."
        self.session.commit()
        self.session.refresh(job)
        return job

    def get_by_job_id(self, job_id: str) -> Job | None:
        """Return one job by public job id."""
        return self.session.query(Job).filter(Job.job_id == job_id).one_or_none()

    def list_for_target(self, target_id: str, limit: int = 50) -> list[Job]:
        """Return recent jobs for a target."""
        bounded_limit = min(max(limit, 1), 500)
        return (
            self.session.query(Job)
            .filter(Job.target_id == target_id)
            .order_by(desc(Job.created_at), desc(Job.id))
            .limit(bounded_limit)
            .all()
        )

    def list_active_for_target(self, target_id: str, limit: int = 50) -> list[Job]:
        """Return queued/running jobs that can receive a cooperative stop request."""
        bounded_limit = min(max(limit, 1), 500)
        return (
            self.session.query(Job)
            .filter(Job.target_id == target_id)
            .filter(Job.status.in_((JOB_STATUS_QUEUED, JOB_STATUS_RUNNING)))
            .order_by(desc(Job.created_at), desc(Job.id))
            .limit(bounded_limit)
            .all()
        )

    def request_stop_for_target(self, target_id: str, reason: str = "operator_requested_stop") -> list[Job]:
        """Mark active target jobs as stop-requested, stopping queued jobs immediately."""
        active_jobs = self.list_active_for_target(target_id)
        now = datetime.now(timezone.utc)
        for job in active_jobs:
            if job.status == JOB_STATUS_QUEUED:
                job.status = JOB_STATUS_STOPPED
                job.result_status = RESULT_SKIPPED
                job.summary = f"Queued job stopped before execution: {reason}."
                job.error = None
                job.finished_at = now
            else:
                job.summary = f"Cooperative stop requested while running: {reason}."
                job.error = "Stop requested; runner will stop before the next technique boundary."
        self.session.commit()
        for job in active_jobs:
            self.session.refresh(job)
        return active_jobs

    def stop_job(self, job: Job, reason: str = "operator_requested_stop") -> Job:
        """Persist a stopped result for one queued/running job when safe to do so."""
        if job.status == JOB_STATUS_QUEUED:
            job.status = JOB_STATUS_STOPPED
            job.result_status = RESULT_SKIPPED
            job.summary = f"Queued job stopped before execution: {reason}."
            job.error = None
            job.finished_at = datetime.now(timezone.utc)
        elif job.status == JOB_STATUS_RUNNING:
            job.summary = f"Cooperative stop requested while running: {reason}."
            job.error = "Stop requested; runner will stop before the next technique boundary."
        else:
            job.error = job.error or "Stop request ignored because job is already terminal."
        self.session.commit()
        self.session.refresh(job)
        return job
