"""Demo worker fixture contract tests."""

from app.contracts.evidence_contract import RESULT_FAILED, RESULT_SKIPPED
from app.contracts.technique_contract import (
    BaseTechnique,
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
    TechniqueExecutionContext,
)
from app.core.permission_levels import PERMISSION_PASSIVE
from app.workers.demo_worker import DemoWorker


class DemoFixtureTechnique(BaseTechnique):
    technique_id = "test.demo_fixture"
    module_id = "test"
    display_name = "Demo Fixture"
    description = "Demo"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "demo"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True
    can_run_in_demo = True
    demo_behavior = {"fixture": "osint_domain_basic.json"}

    def execute(self, context: TechniqueExecutionContext):  # type: ignore[no-untyped-def]
        raise AssertionError("execute must not be called")


class NoDemoTechnique(DemoFixtureTechnique):
    technique_id = "test.no_demo"
    can_run_in_demo = False


class MissingFixtureTechnique(DemoFixtureTechnique):
    technique_id = "test.missing_fixture"
    demo_behavior = {"fixture": "missing.json"}


def _context() -> TechniqueExecutionContext:
    return TechniqueExecutionContext(
        target_id="target-1",
        run_id="run-1",
        mode="demo",
        demo=True,
        dry_run=False,
    )


def test_demo_worker_loads_fixture() -> None:
    result = DemoWorker().run_technique(DemoFixtureTechnique(), _context())

    assert result.status == "success"
    assert result.summary == "Demo fixture loaded: osint_domain_basic.json"


def test_demo_worker_fixture_result_is_skipped() -> None:
    result = DemoWorker().run_technique(DemoFixtureTechnique(), _context())

    assert result.result_status == RESULT_SKIPPED


def test_demo_worker_fixture_result_contains_one_evidence_record() -> None:
    result = DemoWorker().run_technique(DemoFixtureTechnique(), _context())

    assert len(result.evidence) == 1


def test_demo_worker_fixture_evidence_is_demo() -> None:
    result = DemoWorker().run_technique(DemoFixtureTechnique(), _context())

    assert result.evidence[0].demo is True


def test_demo_worker_fixture_evidence_is_not_real_execution() -> None:
    result = DemoWorker().run_technique(DemoFixtureTechnique(), _context())

    assert result.evidence[0].real_execution is False


def test_demo_worker_raw_result_is_not_real_execution() -> None:
    result = DemoWorker().run_technique(DemoFixtureTechnique(), _context())

    assert result.raw_result["real_execution"] is False


def test_demo_worker_returns_failed_when_technique_is_not_demo_allowed() -> None:
    result = DemoWorker().run_technique(NoDemoTechnique(), _context())

    assert result.status == "failed"
    assert result.result_status == RESULT_FAILED


def test_demo_worker_returns_failed_when_fixture_is_missing() -> None:
    result = DemoWorker().run_technique(MissingFixtureTechnique(), _context())

    assert result.status == "failed"
    assert result.result_status == RESULT_FAILED
