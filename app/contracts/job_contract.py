"""Job contract definitions for Ojo de Dios."""

from dataclasses import dataclass, field
from typing import Any

from app.contracts.evidence_contract import VALID_RESULT_STATUSES
from app.core.errors import ContractError

JOB_MODE_DEMO = "demo"
JOB_MODE_DRY_RUN = "dry_run"
JOB_MODE_CONTROLLED = "controlled"
JOB_MODE_EXPERT = "expert"

VALID_JOB_MODES = {
    JOB_MODE_DEMO,
    JOB_MODE_DRY_RUN,
    JOB_MODE_CONTROLLED,
    JOB_MODE_EXPERT,
}

JOB_STATUS_QUEUED = "queued"
JOB_STATUS_RUNNING = "running"
JOB_STATUS_SUCCESS = "success"
JOB_STATUS_PARTIAL = "partial"
JOB_STATUS_FAILED = "failed"
JOB_STATUS_STOPPED = "stopped"
JOB_STATUS_MANUAL_REQUIRED = "manual_required"

VALID_JOB_STATUSES = {
    JOB_STATUS_QUEUED,
    JOB_STATUS_RUNNING,
    JOB_STATUS_SUCCESS,
    JOB_STATUS_PARTIAL,
    JOB_STATUS_FAILED,
    JOB_STATUS_STOPPED,
    JOB_STATUS_MANUAL_REQUIRED,
}


@dataclass
class JobRequest:
    """Request to run selected modules or techniques against a target."""

    job_id: str
    target_id: str
    created_by: str
    mode: str
    selected_modules: list[str] = field(default_factory=list)
    selected_techniques: list[str] = field(default_factory=list)
    permissions_snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass
class JobResult:
    """Result summary for a completed or stopped job."""

    job_id: str
    status: str
    result_status: str
    evidence_ids: list[str] = field(default_factory=list)
    summary: str = ""
    error: str | None = None


def validate_job_request(request: JobRequest) -> None:
    """Validate a job request contract."""
    if not request.job_id:
        raise ContractError("Job id cannot be empty.")
    if not request.target_id:
        raise ContractError("Target id cannot be empty.")
    if not request.created_by:
        raise ContractError("Created by cannot be empty.")
    if request.mode not in VALID_JOB_MODES:
        raise ContractError("Invalid job mode.")


def validate_job_result(result: JobResult) -> None:
    """Validate a job result contract."""
    if not result.job_id:
        raise ContractError("Job id cannot be empty.")
    if result.status not in VALID_JOB_STATUSES:
        raise ContractError("Invalid job status.")
    if result.result_status not in VALID_RESULT_STATUSES:
        raise ContractError("Invalid result status.")
