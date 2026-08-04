"""Ensure strategy planning never calls execution hooks."""

from app.contracts.technique_contract import (
    BaseTechnique,
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
    TechniqueExecutionContext,
    TechniqueExecutionResult,
)
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_DRY_RUN, TargetRecord
from app.core.technique_registry import create_empty_registry
from app.core.x5_strategy_engine import X5StrategyEngine


class ExplodingTechnique(BaseTechnique):
    technique_id = "test.exploding"
    module_id = "test"
    display_name = "Exploding Dummy"
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

    def prepare(self, context: TechniqueExecutionContext) -> TechniqueExecutionContext:
        raise AssertionError("prepare must not be called")

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        raise AssertionError("execute must not be called")

    def parse_result(self, raw_result) -> TechniqueExecutionResult:
        raise AssertionError("parse_result must not be called")


def test_strategy_engine_does_not_call_execution_hooks() -> None:
    registry = create_empty_registry()
    registry.register(ExplodingTechnique)
    target = TargetRecord(
        target_id="target-1",
        name="Example",
        target_type=TARGET_DOMAIN,
        value="example.com",
        normalized_value="example.com",
        mode=TARGET_MODE_DRY_RUN,
    )
    plan = X5StrategyEngine(registry).plan_for_target(target)
    assert len(plan.steps) == 1
    assert plan.steps[0].technique_id == "test.exploding"
    assert plan.steps[0].can_run_now is True
