"""Strategy planning engine for registered techniques."""

from dataclasses import dataclass, field

from app.core.job_state import (
    PLAN_STATUS_INVALID_TARGET,
    PLAN_STATUS_NO_TECHNIQUES_AVAILABLE,
    PLAN_STATUS_PLANNED,
)
from app.core.policy_engine import evaluate_execution_permission
from app.core.target_model import TargetRecord, is_valid_target_mode, is_valid_target_type
from app.core.technique_registry import TechniqueRegistry


@dataclass
class StrategyPlanStep:
    """Single planned technique step."""

    step: int
    technique_id: str
    module_id: str
    display_name: str
    implementation_status: str
    permission_level: str
    requires_confirmation: bool
    requires_user_logic: bool
    can_run_now: bool
    blocked_reason: str | None
    reason: str
    expected_evidence: list[str] = field(default_factory=list)
    required_inputs: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)


@dataclass
class StrategyPlan:
    """Plan produced for a target and registry snapshot."""

    target_id: str
    target_type: str
    mode: str
    status: str
    steps: list[StrategyPlanStep] = field(default_factory=list)
    reason: str = ""

    @property
    def runnable_steps(self) -> list[StrategyPlanStep]:
        """Return steps that X5 can hand to JobRunner now."""
        return [step for step in self.steps if step.can_run_now]

    @property
    def blocked_steps(self) -> list[StrategyPlanStep]:
        """Return steps blocked by policy, scope or missing inputs."""
        return [step for step in self.steps if not step.can_run_now]

    @property
    def runnable_step_count(self) -> int:
        """Return the number of runnable steps."""
        return len(self.runnable_steps)

    @property
    def blocked_step_count(self) -> int:
        """Return the number of blocked steps."""
        return len(self.blocked_steps)

    @property
    def can_execute(self) -> bool:
        """Return whether the plan contains at least one runnable step."""
        return self.runnable_step_count > 0

    @property
    def blocked_reasons(self) -> list[str]:
        """Return unique blocked reasons in plan order."""
        reasons: list[str] = []
        for step in self.blocked_steps:
            if step.blocked_reason and step.blocked_reason not in reasons:
                reasons.append(step.blocked_reason)
        return reasons


class X5StrategyEngine:
    """Build non-executing plans from registered technique metadata."""

    def __init__(self, registry: TechniqueRegistry) -> None:
        self.registry = registry

    def plan_for_target(
        self,
        target: TargetRecord,
        confirmed: bool = False,
        allowlisted_target: bool = True,
        hardware_available: bool = True,
        network_available: bool = True,
        user_logic_available: bool = False,
    ) -> StrategyPlan:
        """Plan matching registered techniques for a target without execution."""
        if not is_valid_target_type(target.target_type) or not is_valid_target_mode(target.mode):
            return StrategyPlan(
                target_id=target.target_id,
                target_type=target.target_type,
                mode=target.mode,
                status=PLAN_STATUS_INVALID_TARGET,
                reason="Target type or mode is invalid.",
            )

        technique_classes = self.registry.list_all()
        if target.allowed_modules:
            allowed_modules = set(target.allowed_modules)
            technique_classes = [
                technique_cls
                for technique_cls in technique_classes
                if technique_cls().module_id in allowed_modules
            ]

        if not technique_classes:
            return StrategyPlan(
                target_id=target.target_id,
                target_type=target.target_type,
                mode=target.mode,
                status=PLAN_STATUS_NO_TECHNIQUES_AVAILABLE,
                reason="No registered techniques are available for this target.",
            )

        available_inputs = {
            "target",
            "target_id",
            "target_type",
            "value",
            "normalized_value",
            "mode",
            *target.metadata.keys(),
        }
        steps: list[StrategyPlanStep] = []
        for technique_cls in sorted(technique_classes, key=lambda cls: cls().technique_id):
            technique = technique_cls()
            technique.validate_metadata()
            profile = technique.get_permission_profile()
            decision = evaluate_execution_permission(
                profile=profile,
                execution_mode=target.mode,
                confirmed=confirmed,
                allowlisted_target=allowlisted_target,
                hardware_available=hardware_available,
                network_available=network_available,
                user_logic_available=user_logic_available,
            )
            required_inputs = list(technique.required_inputs)
            missing_inputs = [required_input for required_input in required_inputs if required_input not in available_inputs]
            if missing_inputs:
                can_run_now = False
                blocked_reason = "MISSING_INPUT"
                reason = "Missing required inputs."
            elif not decision.allowed:
                can_run_now = False
                blocked_reason = decision.blocked_reason
                reason = decision.reason
            else:
                can_run_now = True
                blocked_reason = None
                reason = "Technique matches target scope and policy."

            steps.append(
                StrategyPlanStep(
                    step=len(steps) + 1,
                    technique_id=technique.technique_id,
                    module_id=technique.module_id,
                    display_name=technique.display_name,
                    implementation_status=technique.implementation_status,
                    permission_level=technique.permission_level,
                    requires_confirmation=technique.requires_confirmation,
                    requires_user_logic=technique.requires_user_implementation,
                    can_run_now=can_run_now,
                    blocked_reason=blocked_reason,
                    reason=reason,
                    expected_evidence=list(technique.expected_evidence),
                    required_inputs=required_inputs,
                    missing_inputs=missing_inputs,
                )
            )

        return StrategyPlan(
            target_id=target.target_id,
            target_type=target.target_type,
            mode=target.mode,
            status=PLAN_STATUS_PLANNED,
            steps=steps,
            reason="Plan created from registered technique metadata.",
        )
