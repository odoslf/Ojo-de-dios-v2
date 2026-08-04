"""JobRunner manual-required result tests."""

from app.contracts.evidence_contract import RESULT_FAILED, RESULT_MANUAL_REQUIRED
from app.contracts.job_contract import (
    JOB_STATUS_FAILED,
    JOB_STATUS_MANUAL_REQUIRED,
    JobRequest,
)
from app.contracts.technique_contract import (
    BaseTechnique,
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
)
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.technique_registry import TechniqueRegistry
from app.workers.job_runner import JobRunner


class ManualRequiredTechnique(BaseTechnique):
    technique_id = "test.manual_required"
    module_id = "test"
    display_name = "Manual Required"
    description = "Manual required"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True


def _registry() -> TechniqueRegistry:
    registry = TechniqueRegistry()
    registry.register(ManualRequiredTechnique)
    return registry


def test_job_runner_returns_manual_required_for_unimplemented_technique() -> None:
    runner = JobRunner(_registry())
    request = JobRequest(
        job_id="job-1",
        target_id="target-1",
        created_by="tester",
        mode="controlled",
        selected_techniques=["test.manual_required"],
        permissions_snapshot={"confirmed": True},
    )

    result = runner.run_job(request)

    assert result.status == JOB_STATUS_MANUAL_REQUIRED
    assert result.result_status == RESULT_MANUAL_REQUIRED
    assert "IMPLEMENTACION_USUARIO_REQUERIDA" in result.summary


def test_job_runner_fails_when_no_techniques_are_selected() -> None:
    runner = JobRunner(_registry())
    request = JobRequest(
        job_id="job-1",
        target_id="target-1",
        created_by="tester",
        mode="controlled",
        selected_techniques=[],
        permissions_snapshot={"confirmed": True},
    )

    result = runner.run_job(request)

    assert result.status == JOB_STATUS_FAILED
    assert result.result_status == RESULT_FAILED
    assert result.error == "No techniques selected."
