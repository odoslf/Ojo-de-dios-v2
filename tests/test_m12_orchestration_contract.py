import pytest

from app.contracts.evidence_contract import EVIDENCE_QUALITY_HIGH, EvidenceRecord, RESULT_SUCCESS
from app.contracts.technique_contract import BaseTechnique, STATUS_READY_CONTROLLED, TechniqueExecutionContext
from app.core.kill_switch import KillSwitchController
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.registry_loader import load_registry_from_package
from app.core.target_model import TARGET_CUSTOM, TargetRecord
from app.core.technique_registry import TechniqueRegistry
from app.modules.m12_orchestration.orchestrator import (
    M12_ALLOWED_MODULES,
    M12_EXECUTABLE_MODULES,
    M12PersistentPlanStore,
    build_m12_execution_timeline,
    build_m12_orchestration_plan,
    run_m12_orchestration_plan,
)


class M03RunnableTechnique(BaseTechnique):
    technique_id = "test.m03.passive"
    module_id = "m03_network_services"
    display_name = "M03 passive test"
    description = "Passive test technique"
    tool_name = "internal"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    required_inputs = ["service_fingerprints"]
    expected_evidence = ["service_map"]
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    requires_network = False

    def execute(self, context: TechniqueExecutionContext):
        evidence = EvidenceRecord(
            evidence_id=f"ev-{context.run_id}",
            run_id=context.run_id,
            target_id=context.target_id,
            technique_id=self.technique_id,
            module_id=self.module_id,
            evidence_type="service_map",
            quality=EVIDENCE_QUALITY_HIGH,
            summary="passive m03 evidence",
            content={"service_fingerprints": context.parameters["service_fingerprints"]},
            source="test",
        )
        from app.contracts.technique_contract import TechniqueExecutionResult

        return TechniqueExecutionResult(self.technique_id, self.module_id, RESULT_SUCCESS, evidence.summary, [evidence], evidence.content)


class AttackModuleTechnique(M03RunnableTechnique):
    technique_id = "test.m04.attack"
    module_id = "m04_web_intrusion"


def _registry() -> TechniqueRegistry:
    registry = TechniqueRegistry()
    registry.register(M03RunnableTechnique)
    registry.register(AttackModuleTechnique)
    return registry


def _target() -> TargetRecord:
    return TargetRecord(
        target_id="target-1",
        name="target",
        target_type=TARGET_CUSTOM,
        value="target",
        normalized_value="target",
        mode="controlled",
        allowed_modules=list(M12_ALLOWED_MODULES),
        metadata={"service_fingerprints": [{"host": "10.0.0.5", "port": 443}]},
    )


def test_m12_registers_orchestration_plan_technique_without_attack_modules() -> None:
    registry = load_registry_from_package("app.modules.m12_orchestration")

    assert registry.list_ids() == ["orchestration.x5.plan_allowed_modules"]
    technique = registry.require("orchestration.x5.plan_allowed_modules")()
    technique.validate_metadata()
    assert technique.module_id == "m12_orchestration"
    assert technique.permission_level == PERMISSION_PASSIVE
    assert technique.requires_network is False
    assert technique.requires_user_implementation is False


def test_m12_plan_filters_to_allowed_implemented_modules() -> None:
    plan = build_m12_orchestration_plan(_target(), _registry(), requested_modules=["m03_network_services"], m16_readiness={"status": "READY", "checks": []})

    assert plan.execution_implied is False
    assert plan.requested_modules == ("m03_network_services",)
    assert [step.technique_id for step in plan.steps] == ["test.m03.passive"]
    assert plan.runnable_steps[0].module_id in M12_EXECUTABLE_MODULES
    assert plan.m16_readiness == {"status": "READY", "check_count": 0, "execution_implied": False}


def test_m12_rejects_attack_module_requests() -> None:
    with pytest.raises(Exception, match="M12 can only orchestrate"):
        build_m12_orchestration_plan(_target(), _registry(), requested_modules=["m04_web_intrusion"], m16_readiness={"status": "READY", "checks": []})


def test_m12_run_executes_runnable_steps_through_job_runner() -> None:
    plan = build_m12_orchestration_plan(_target(), _registry(), requested_modules=["m03_network_services"], m16_readiness={"status": "READY", "checks": []})

    summary = run_m12_orchestration_plan(
        plan,
        _registry(),
        parameters_by_technique={"test.m03.passive": {"service_fingerprints": [{"host": "10.0.0.5", "port": 443}]}},
        kill_switch=KillSwitchController(),
    )

    assert summary.execution_performed is True
    assert summary.status == "success"
    assert summary.job_results[0].result_status == RESULT_SUCCESS
    assert summary.evidence_ids == (f"ev-{plan.plan_id}-step-1",)


def test_m12_run_honors_kill_switch_without_executing() -> None:
    kill_switch = KillSwitchController()
    kill_switch.activate("test stop", activated_by="test")
    plan = build_m12_orchestration_plan(_target(), _registry(), requested_modules=["m03_network_services"], m16_readiness={"status": "READY", "checks": []})

    summary = run_m12_orchestration_plan(plan, _registry(), kill_switch=kill_switch)

    assert summary.execution_performed is True
    assert summary.status == "failed"
    assert summary.job_results[0].error == "Kill switch active: new jobs are blocked."
    assert summary.evidence_ids == ()


class FakeScoringEngine:
    def __init__(self):
        self.events = []

    def update_after_result(self, event):
        self.events.append(event)
        return {"technique_id": event.technique_id, "result_status": event.result_status, "evidence_ids": list(event.evidence_ids)}


def test_m12_run_updates_optional_scoring_engine_after_result() -> None:
    plan = build_m12_orchestration_plan(_target(), _registry(), requested_modules=["m03_network_services"], m16_readiness={"status": "READY", "checks": []})
    scoring = FakeScoringEngine()

    summary = run_m12_orchestration_plan(
        plan,
        _registry(),
        parameters_by_technique={"test.m03.passive": {"service_fingerprints": [{"host": "10.0.0.5", "port": 443}]}},
        kill_switch=KillSwitchController(),
        scoring_engine=scoring,
    )

    assert scoring.events[0].technique_id == "test.m03.passive"
    assert scoring.events[0].evidence_ids == [f"ev-{plan.plan_id}-step-1"]
    assert summary.scoring_updates[0]["result_status"] == RESULT_SUCCESS


def test_m12_persistent_plan_store_survives_new_instance(tmp_path) -> None:
    plan = build_m12_orchestration_plan(
        _target(),
        _registry(),
        requested_modules=["m03_network_services"],
        plan_id="plan-persist-1",
        m16_readiness={"status": "READY", "checks": []},
    )
    first_store = M12PersistentPlanStore(tmp_path / "plans.sqlite3")
    first_store.save_plan(plan)

    second_store = M12PersistentPlanStore(tmp_path / "plans.sqlite3")
    payload = second_store.load_plan_payload("plan-persist-1")

    assert payload["plan_id"] == "plan-persist-1"
    assert payload["target_id"] == "target-1"
    assert payload["steps"][0]["technique_id"] == "test.m03.passive"


def test_m12_run_honors_persistent_cancellation_before_next_job(tmp_path) -> None:
    plan = build_m12_orchestration_plan(
        _target(),
        _registry(),
        requested_modules=["m03_network_services"],
        plan_id="plan-cancel-1",
        m16_readiness={"status": "READY", "checks": []},
    )
    store = M12PersistentPlanStore(tmp_path / "plans.sqlite3")
    store.save_plan(plan)
    store.request_cancel(plan.plan_id, "operator stop", requested_by="tester")

    summary = run_m12_orchestration_plan(
        plan,
        _registry(),
        parameters_by_technique={"test.m03.passive": {"service_fingerprints": [{"host": "10.0.0.5", "port": 443}]}},
        kill_switch=KillSwitchController(),
        plan_store=store,
    )
    payload = store.load_plan_payload(plan.plan_id)

    assert summary.canceled is True
    assert summary.status == "canceled"
    assert summary.job_results == ()
    assert store.is_cancel_requested(plan.plan_id) is True
    assert payload["plan_id"] == plan.plan_id
    assert store.load_plan_payload(plan.plan_id)["status"] == "canceled"

class FlakyRetryTechnique(M03RunnableTechnique):
    technique_id = "test.m03.flaky"
    attempts = 0

    def execute(self, context: TechniqueExecutionContext):
        FlakyRetryTechnique.attempts += 1
        if FlakyRetryTechnique.attempts == 1:
            raise RuntimeError("temporary failure")
        return super().execute(context)


class DependentTechnique(M03RunnableTechnique):
    technique_id = "test.m03.zz_dependent"


def _retry_registry(include_dependent: bool = True) -> TechniqueRegistry:
    registry = TechniqueRegistry()
    registry.register(FlakyRetryTechnique)
    if include_dependent:
        registry.register(DependentTechnique)
    return registry


def test_m12_retries_failed_step_until_success() -> None:
    FlakyRetryTechnique.attempts = 0
    plan = build_m12_orchestration_plan(_target(), _retry_registry(include_dependent=False), requested_modules=["m03_network_services"], m16_readiness={"status": "READY", "checks": []})

    summary = run_m12_orchestration_plan(
        plan,
        _retry_registry(include_dependent=False),
        parameters_by_technique={"test.m03.flaky": {"service_fingerprints": [{"host": "10.0.0.5", "port": 443}]}},
        retry_policy={"test.m03.flaky": 2},
        kill_switch=KillSwitchController(),
    )

    assert FlakyRetryTechnique.attempts == 2
    assert summary.status == "success"
    assert [item["attempt"] for item in summary.step_attempts] == [1, 2]
    assert summary.step_attempts[0]["status"] == "failed"
    assert summary.step_attempts[1]["status"] == "success"


def test_m12_skips_step_when_dependency_status_not_satisfied() -> None:
    FlakyRetryTechnique.attempts = 0
    plan = build_m12_orchestration_plan(_target(), _retry_registry(), requested_modules=["m03_network_services"], m16_readiness={"status": "READY", "checks": []})

    summary = run_m12_orchestration_plan(
        plan,
        _retry_registry(),
        parameters_by_technique={"test.m03.flaky": {"service_fingerprints": [{"host": "10.0.0.5", "port": 443}]}, "test.m03.zz_dependent": {"service_fingerprints": [{"host": "10.0.0.5", "port": 443}]}},
        retry_policy={"test.m03.flaky": 1},
        step_dependencies={"test.m03.zz_dependent": {"depends_on": "test.m03.flaky", "required_status": "success"}},
        kill_switch=KillSwitchController(),
    )

    assert summary.status == "failed"
    assert summary.job_results[-1].error == "dependency_not_satisfied"
    assert summary.step_attempts[-1] == {"technique_id": "test.m03.zz_dependent", "attempt": 0, "status": "skipped", "dependency": "test.m03.flaky"}


def test_m12_execution_timeline_includes_attempts_results_and_completion() -> None:
    FlakyRetryTechnique.attempts = 0
    plan = build_m12_orchestration_plan(_target(), _retry_registry(include_dependent=False), requested_modules=["m03_network_services"], plan_id="plan-timeline-1", m16_readiness={"status": "READY", "checks": []})
    summary = run_m12_orchestration_plan(
        plan,
        _retry_registry(include_dependent=False),
        parameters_by_technique={"test.m03.flaky": {"service_fingerprints": [{"host": "10.0.0.5", "port": 443}]}},
        retry_policy={"test.m03.flaky": 2},
        kill_switch=KillSwitchController(),
    )

    timeline = build_m12_execution_timeline(plan, summary)

    assert timeline["plan_id"] == "plan-timeline-1"
    assert timeline["status"] == "success"
    assert [event["event_type"] for event in timeline["events"]] == ["plan_created", "step_attempt", "step_attempt", "job_result", "run_completed"]
    assert timeline["events"][1]["detail"] == "attempt=1 status=failed"
    assert timeline["events"][-1]["evidence_ids"] == list(summary.evidence_ids)


def test_m12_execution_timeline_marks_dependency_skips() -> None:
    FlakyRetryTechnique.attempts = 0
    plan = build_m12_orchestration_plan(_target(), _retry_registry(), requested_modules=["m03_network_services"], plan_id="plan-timeline-2", m16_readiness={"status": "READY", "checks": []})
    summary = run_m12_orchestration_plan(
        plan,
        _retry_registry(),
        parameters_by_technique={"test.m03.flaky": {"service_fingerprints": [{"host": "10.0.0.5", "port": 443}]}, "test.m03.zz_dependent": {"service_fingerprints": [{"host": "10.0.0.5", "port": 443}]}},
        retry_policy={"test.m03.flaky": 1},
        step_dependencies={"test.m03.zz_dependent": {"depends_on": "test.m03.flaky", "required_status": "success"}},
        kill_switch=KillSwitchController(),
    )

    timeline = build_m12_execution_timeline(plan, summary)
    skipped = [event for event in timeline["events"] if event["event_type"] == "step_skipped"]

    assert skipped[0]["technique_id"] == "test.m03.zz_dependent"
    assert skipped[0]["detail"] == "attempt=0 status=skipped dependency=test.m03.flaky"
    assert timeline["events"][-1]["status"] == "failed"
