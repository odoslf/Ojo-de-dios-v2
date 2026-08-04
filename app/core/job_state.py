"""Planning and job state constants for local persisted job execution."""

from dataclasses import dataclass

PLAN_STATUS_PLANNED = "planned"
PLAN_STATUS_NO_TECHNIQUES_AVAILABLE = "no_techniques_available"
PLAN_STATUS_INVALID_TARGET = "invalid_target"

JOB_START_NOT_AVAILABLE = "job_start_not_available"
JOB_STOP_NOT_AVAILABLE = "job_stop_not_available"

JOB_RUNNER_NOT_STARTED = "not_started"
JOB_RUNNER_RUNNING = "running"
JOB_RUNNER_FINISHED = "finished"
JOB_RUNNER_STOPPED = "stopped"

JOB_EXECUTION_DEMO = "demo"
JOB_EXECUTION_DRY_RUN = "dry_run"
JOB_EXECUTION_MANUAL_REQUIRED = "manual_required"
JOB_EXECUTION_SUCCESS = "success"
JOB_EXECUTION_FAILED = "failed"


@dataclass
class JobStateSnapshot:
    """Snapshot for local persisted job runtime state."""

    job_id: str | None = None
    target_id: str | None = None
    status: str = JOB_RUNNER_NOT_STARTED
    message: str = "JobRunner is ready for local persisted jobs; no run has started for this snapshot."
