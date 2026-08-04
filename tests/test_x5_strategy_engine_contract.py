"""Contract tests for registry-backed strategy planning."""

from app.contracts.technique_contract import BaseTechnique, STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
from app.core.job_state import PLAN_STATUS_NO_TECHNIQUES_AVAILABLE, PLAN_STATUS_PLANNED
from app.core.permission_levels import BLOCKED_NEEDS_CONFIRMATION, PERMISSION_ACTIVE_SENSITIVE, PERMISSION_PASSIVE
from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_CONTROLLED, TARGET_MODE_DRY_RUN, TargetRecord
from app.core.technique_registry import create_empty_registry
from app.core.x5_strategy_engine import X5StrategyEngine


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


class DummyWebTechnique(BaseTechnique):
    technique_id = "test.web"
    module_id = "web"
    display_name = "Web Dummy"
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


class SensitiveTechnique(BaseTechnique):
    technique_id = "test.sensitive"
    module_id = "web"
    display_name = "Sensitive Dummy"
    description = "Dummy"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "none"
    permission_level = PERMISSION_ACTIVE_SENSITIVE
    required_inputs = ["target"]
    expected_evidence = ["dummy_evidence"]
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True
    requires_confirmation = True


class MissingInputTechnique(BaseTechnique):
    technique_id = "test.missing"
    module_id = "osint"
    display_name = "Missing Input Dummy"
    description = "Dummy"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "none"
    permission_level = PERMISSION_PASSIVE
    required_inputs = ["missing_field"]
    expected_evidence = ["dummy_evidence"]
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True


def make_target(*, mode: str = TARGET_MODE_DRY_RUN, allowed_modules: list[str] | None = None) -> TargetRecord:
    return TargetRecord(
        target_id="target-1",
        name="Example",
        target_type=TARGET_DOMAIN,
        value="example.com",
        normalized_value="example.com",
        mode=mode,
        allowed_modules=allowed_modules or [],
    )


def test_empty_registry_returns_no_techniques_available() -> None:
    engine = X5StrategyEngine(create_empty_registry())
    plan = engine.plan_for_target(make_target())
    assert plan.status == PLAN_STATUS_NO_TECHNIQUES_AVAILABLE
    assert plan.steps == []


def test_allowed_modules_filters_registered_techniques() -> None:
    registry = create_empty_registry()
    registry.register_many([DummyOsintTechnique, DummyWebTechnique])
    plan = X5StrategyEngine(registry).plan_for_target(make_target(allowed_modules=["osint"]))
    assert plan.status == PLAN_STATUS_PLANNED
    assert [step.technique_id for step in plan.steps] == ["test.osint"]


def test_empty_allowed_modules_considers_all_registered_techniques() -> None:
    registry = create_empty_registry()
    registry.register_many([DummyOsintTechnique, DummyWebTechnique])
    plan = X5StrategyEngine(registry).plan_for_target(make_target())
    assert [step.technique_id for step in plan.steps] == ["test.osint", "test.web"]


def test_sensitive_technique_requires_confirmation_in_controlled_mode() -> None:
    registry = create_empty_registry()
    registry.register(SensitiveTechnique)
    plan = X5StrategyEngine(registry).plan_for_target(make_target(mode=TARGET_MODE_CONTROLLED), confirmed=False)
    assert plan.steps[0].can_run_now is False
    assert plan.steps[0].blocked_reason == BLOCKED_NEEDS_CONFIRMATION


def test_sensitive_technique_allows_when_confirmed_in_controlled_mode() -> None:
    registry = create_empty_registry()
    registry.register(SensitiveTechnique)
    plan = X5StrategyEngine(registry).plan_for_target(make_target(mode=TARGET_MODE_CONTROLLED), confirmed=True)
    assert plan.steps[0].can_run_now is True
    assert plan.steps[0].blocked_reason is None


def test_missing_input_blocks_step() -> None:
    registry = create_empty_registry()
    registry.register(MissingInputTechnique)
    plan = X5StrategyEngine(registry).plan_for_target(make_target())
    assert plan.steps[0].can_run_now is False
    assert plan.steps[0].blocked_reason == "MISSING_INPUT"
    assert plan.steps[0].missing_inputs == ["missing_field"]


def test_plan_exposes_runnable_and_blocked_summary() -> None:
    registry = create_empty_registry()
    registry.register_many([DummyOsintTechnique, MissingInputTechnique])
    plan = X5StrategyEngine(registry).plan_for_target(make_target())
    assert plan.runnable_step_count == 1
    assert plan.blocked_step_count == 1
    assert plan.can_execute is True
    assert plan.blocked_reasons == ["MISSING_INPUT"]
    assert [step.technique_id for step in plan.runnable_steps] == ["test.osint"]
    assert [step.technique_id for step in plan.blocked_steps] == ["test.missing"]
