"""JobRunner kill switch contract tests."""

from app.contracts.evidence_contract import RESULT_FAILED
from app.contracts.job_contract import JOB_STATUS_STOPPED, JobRequest
from app.contracts.technique_contract import (
    BaseTechnique,
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
    TechniqueExecutionContext,
)
from app.core.kill_switch import KillSwitchController
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.technique_registry import TechniqueRegistry
from app.workers.job_runner import JobRunner


class ExplodingTechnique(BaseTechnique):
    technique_id = "test.exploding"
    module_id = "test"
    display_name = "Exploding"
    description = "Exploding"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True

    def execute(self, context: TechniqueExecutionContext):  # type: ignore[no-untyped-def]
        raise AssertionError("execute must not be called")


def test_job_runner_blocks_before_resolving_execution_when_kill_switch_is_active() -> None:
    registry = TechniqueRegistry()
    registry.register(ExplodingTechnique)
    controller = KillSwitchController()
    controller.activate("test", "tester")
    runner = JobRunner(registry, kill_switch=controller)
    request = JobRequest(
        job_id="job-1",
        target_id="target-1",
        created_by="tester",
        mode="controlled",
        selected_techniques=["test.exploding"],
    )

    result = runner.run_job(request)

    assert result.status == JOB_STATUS_STOPPED
    assert result.result_status == RESULT_FAILED
    assert "Kill switch active" in result.error
