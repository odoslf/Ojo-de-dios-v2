"""Contract tests for the router planning facade."""

from app.contracts.technique_contract import BaseTechnique, STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
from app.core.job_state import PLAN_STATUS_NO_TECHNIQUES_AVAILABLE, PLAN_STATUS_PLANNED
from app.core.ojo_router import OjoRouter
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_DRY_RUN, TargetRecord
from app.core.technique_registry import create_empty_registry


class DummyOsintTechnique(BaseTechnique):
    technique_id = "test.osint"
    module_id = "osint"
    display_name = "OSINT Dummy"
    description = "Dummy"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "none"
    permission_level = PERMISSION_PASSIVE
    required_inputs = ["target"]
    expected_evidence = ["dummy_evidence"]
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True


def make_target() -> TargetRecord:
    return TargetRecord(
        target_id="target-1",
        name="Example",
        target_type=TARGET_DOMAIN,
        value="example.com",
        normalized_value="example.com",
        mode=TARGET_MODE_DRY_RUN,
    )


def test_default_router_starts_with_empty_registry() -> None:
    router = OjoRouter()
    assert router.list_registered_technique_ids() == []
    assert router.plan_target(make_target()).status == PLAN_STATUS_NO_TECHNIQUES_AVAILABLE


def test_router_with_registry_returns_plan() -> None:
    registry = create_empty_registry()
    registry.register(DummyOsintTechnique)
    router = OjoRouter(registry)
    plan = router.plan_target(make_target())
    assert plan.status == PLAN_STATUS_PLANNED
    assert [step.technique_id for step in plan.steps] == ["test.osint"]


def test_runtime_state_reports_no_active_jobs() -> None:
    runtime_state = OjoRouter().get_runtime_state()
    assert runtime_state.app_started_at
    assert runtime_state.active_jobs == 0
