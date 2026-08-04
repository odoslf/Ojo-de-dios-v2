"""JobRunner dry-run, demo, and worker resolution tests."""

from app.contracts.evidence_contract import RESULT_FAILED, RESULT_SKIPPED
from app.contracts.job_contract import JOB_STATUS_FAILED, JOB_STATUS_PARTIAL, JOB_STATUS_SUCCESS, JobRequest
from app.contracts.technique_contract import (
    BaseTechnique,
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
    TechniqueExecutionContext,
)
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.technique_registry import TechniqueRegistry
from app.workers.job_runner import JobRunner


class DryRunTechnique(BaseTechnique):
    technique_id = "test.dry_run"
    module_id = "test"
    display_name = "Dry Run"
    description = "Dry run"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True

    def execute(self, context: TechniqueExecutionContext):  # type: ignore[no-untyped-def]
        raise AssertionError("execute must not be called")


class MissingWorkerTechnique(DryRunTechnique):
    technique_id = "test.missing_worker"
    worker = "missing_worker"


class SecondDryRunTechnique(DryRunTechnique):
    technique_id = "test.second_dry_run"


def _registry(*techniques: type[BaseTechnique]) -> TechniqueRegistry:
    registry = TechniqueRegistry()
    for technique in techniques:
        registry.register(technique)
    return registry


def test_job_runner_dry_run_does_not_call_execute() -> None:
    runner = JobRunner(_registry(DryRunTechnique))
    request = JobRequest(
        job_id="job-1",
        target_id="target-1",
        created_by="tester",
        mode="dry_run",
        selected_techniques=["test.dry_run"],
    )

    result = runner.run_job(request)

    assert result.status == JOB_STATUS_SUCCESS
    assert result.result_status == RESULT_SKIPPED


def test_job_runner_demo_does_not_call_execute() -> None:
    runner = JobRunner(_registry(DryRunTechnique))
    request = JobRequest(
        job_id="job-1",
        target_id="target-1",
        created_by="tester",
        mode="demo",
        selected_techniques=["test.dry_run"],
    )

    result = runner.run_job(request)

    assert result.status == JOB_STATUS_SUCCESS
    assert result.result_status == RESULT_SKIPPED


def test_job_runner_fails_when_worker_is_missing() -> None:
    runner = JobRunner(_registry(MissingWorkerTechnique))
    request = JobRequest(
        job_id="job-1",
        target_id="target-1",
        created_by="tester",
        mode="controlled",
        selected_techniques=["test.missing_worker"],
    )

    result = runner.run_job(request)

    assert result.status == JOB_STATUS_FAILED
    assert result.result_status == RESULT_FAILED
    assert "Worker not available" in result.error


def test_job_runner_executes_every_selected_technique_and_keeps_partial_outcomes() -> None:
    runner = JobRunner(_registry(DryRunTechnique, SecondDryRunTechnique, MissingWorkerTechnique))
    request = JobRequest(
        job_id="job-many",
        target_id="target-1",
        created_by="tester",
        mode="dry_run",
        selected_techniques=["test.dry_run", "test.second_dry_run", "test.missing_worker"],
    )

    result = runner.run_job(request)

    assert result.status == JOB_STATUS_PARTIAL
    assert result.result_status == RESULT_FAILED
    assert "test.dry_run: Dry run" in result.summary
    assert "test.second_dry_run: Dry run" in result.summary
    assert "test.missing_worker: Worker not available" in result.summary
