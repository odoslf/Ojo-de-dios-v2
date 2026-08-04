"""Base worker acceptance tests."""

from app.contracts.evidence_contract import RESULT_SKIPPED
from app.contracts.technique_contract import (
    BaseTechnique,
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
    TechniqueExecutionContext,
)
from app.core.permission_levels import PERMISSION_PASSIVE
from app.workers.demo_worker import DemoWorker
from app.workers.windows_worker import WindowsWorker


class WorkerDummyTechnique(BaseTechnique):
    technique_id = "test.worker_dummy"
    module_id = "test"
    display_name = "Worker Dummy"
    description = "Dummy"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True

    def execute(self, context: TechniqueExecutionContext):  # type: ignore[no-untyped-def]
        raise AssertionError("execute must not be called")


def test_windows_worker_accepts_windows_jobs() -> None:
    assert WindowsWorker().can_handle("windows") is True


def test_windows_worker_rejects_docker_jobs() -> None:
    assert WindowsWorker().can_handle("docker") is False


def test_windows_worker_dry_run_does_not_call_execute() -> None:
    context = TechniqueExecutionContext(
        target_id="target-1",
        run_id="job-1",
        mode="dry_run",
        dry_run=True,
    )

    result = WindowsWorker().run_technique(WorkerDummyTechnique(), context)

    assert result.result_status == RESULT_SKIPPED
    assert result.raw_result["real_execution"] is False


def test_demo_worker_demo_does_not_call_execute() -> None:
    context = TechniqueExecutionContext(
        target_id="target-1",
        run_id="job-1",
        mode="demo",
        demo=True,
    )

    result = DemoWorker().run_technique(WorkerDummyTechnique(), context)

    assert result.result_status == RESULT_SKIPPED
    assert result.raw_result["real_execution"] is False
