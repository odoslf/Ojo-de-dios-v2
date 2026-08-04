"""M12 orchestration primitives for supervised runs across implemented modules.

Ronda 15 implements the base coordinator only for modules already promoted in the
roadmap: M01, M03, M09 and M16 readiness.  It does not introduce attack-module
logic, does not synthesize placeholder techniques and does not bypass X5 policy,
TechniqueRegistry, workers, the kill switch or evidence contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
import json
import sqlite3
from typing import Any
from uuid import uuid4

from app.contracts.evidence_contract import EVIDENCE_QUALITY_MEDIUM, EvidenceRecord, RESULT_SKIPPED, RESULT_SUCCESS
from app.contracts.job_contract import JOB_STATUS_FAILED, JOB_STATUS_PARTIAL, JOB_STATUS_SUCCESS, JobRequest, JobResult
from app.contracts.technique_contract import BaseTechnique, STATUS_READY_CONTROLLED, TechniqueExecutionContext, TechniqueExecutionResult
from app.core.errors import ContractError
from app.core.kill_switch import KillSwitchController, get_global_kill_switch
from app.core.ojo_router import OjoRouter
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.scoring_engine import ScoringEvent
from app.core.target_model import TargetRecord
from app.core.technique_registry import TechniqueRegistry
from app.modules.m16_ops_quality.status import build_m16_readiness_report
from app.workers.base_worker import BaseWorker
from app.workers.job_runner import JobRunner

M12_MODULE_ID = "m12_orchestration"
M12_ALLOWED_MODULES: tuple[str, ...] = (
    "m01_osint",
    "m03_network_services",
    "m09_scraping_intelligence",
    "m16_ops_quality",
)
M12_EXECUTABLE_MODULES: tuple[str, ...] = (
    "m01_osint",
    "m03_network_services",
    "m09_scraping_intelligence",
)
M12_WORKER_ALIASES: dict[str, str] = {
    "AIWorker": "ai",
    "EvidenceWorker": "evidence",
    "NetworkExploitWorker": "network_services_passive",
    "PythonToolWorker": "python_tool",
    "ScrapingWorker": "scraping",
    "OpsWorker": "ops",
    "WSLWorker": "wsl",
    "WindowsWorker": "windows",
}


@dataclass(frozen=True, slots=True)
class M12PlanStep:
    """One X5-validated orchestration step."""

    step: int
    technique_id: str
    module_id: str
    worker: str
    can_run_now: bool
    blocked_reason: str | None
    reason: str
    expected_evidence: tuple[str, ...] = ()
    required_inputs: tuple[str, ...] = ()
    missing_inputs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "technique_id": self.technique_id,
            "module_id": self.module_id,
            "worker": self.worker,
            "can_run_now": self.can_run_now,
            "blocked_reason": self.blocked_reason,
            "reason": self.reason,
            "expected_evidence": list(self.expected_evidence),
            "required_inputs": list(self.required_inputs),
            "missing_inputs": list(self.missing_inputs),
        }


@dataclass(frozen=True, slots=True)
class M12OrchestrationPlan:
    """Persistent-safe plan summary produced before any execution."""

    plan_id: str
    target_id: str
    mode: str
    requested_modules: tuple[str, ...]
    status: str
    steps: tuple[M12PlanStep, ...]
    m16_readiness: dict[str, Any]
    execution_implied: bool = False

    @property
    def runnable_steps(self) -> tuple[M12PlanStep, ...]:
        return tuple(step for step in self.steps if step.can_run_now and step.module_id in M12_EXECUTABLE_MODULES)

    @property
    def blocked_steps(self) -> tuple[M12PlanStep, ...]:
        return tuple(step for step in self.steps if not step.can_run_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "target_id": self.target_id,
            "mode": self.mode,
            "requested_modules": list(self.requested_modules),
            "status": self.status,
            "steps": [step.to_dict() for step in self.steps],
            "runnable_step_count": len(self.runnable_steps),
            "blocked_step_count": len(self.blocked_steps),
            "m16_readiness": self.m16_readiness,
            "execution_implied": self.execution_implied,
        }


@dataclass(frozen=True, slots=True)
class M12RunSummary:
    """Aggregate of concrete JobRunner results launched by M12."""

    plan_id: str
    target_id: str
    status: str
    job_results: tuple[JobResult, ...]
    evidence_ids: tuple[str, ...]
    execution_performed: bool
    scoring_updates: tuple[dict[str, Any], ...] = ()
    canceled: bool = False
    step_attempts: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "target_id": self.target_id,
            "status": self.status,
            "job_results": [result.__dict__ for result in self.job_results],
            "evidence_ids": list(self.evidence_ids),
            "execution_performed": self.execution_performed,
            "scoring_updates": list(self.scoring_updates),
            "canceled": self.canceled,
            "step_attempts": list(self.step_attempts),
        }


class M12PersistentPlanStore:
    """SQLite-backed storage for orchestration plans and cancellation state."""

    def __init__(self, sqlite_path: str | Path = "storage/workspaces/m12_orchestration/plans.sqlite3") -> None:
        self.sqlite_path = Path(sqlite_path)
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.sqlite_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS plans (
                    plan_id TEXT PRIMARY KEY,
                    target_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cancellations (
                    plan_id TEXT PRIMARY KEY,
                    requested INTEGER NOT NULL,
                    reason TEXT,
                    requested_at TEXT NOT NULL
                )
                """
            )

    def save_plan(self, plan: M12OrchestrationPlan) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        payload = json.dumps(plan.to_dict(), sort_keys=True, ensure_ascii=False)
        with sqlite3.connect(self.sqlite_path) as connection:
            connection.execute(
                "INSERT INTO plans (plan_id, target_id, status, payload_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(plan_id) DO UPDATE SET status = excluded.status, payload_json = excluded.payload_json, updated_at = excluded.updated_at",
                (plan.plan_id, plan.target_id, plan.status, payload, now, now),
            )
        return {"sqlite_path": self.sqlite_path.as_posix(), "plan_id": plan.plan_id, "stored": True}

    def load_plan_payload(self, plan_id: str) -> dict[str, Any]:
        with sqlite3.connect(self.sqlite_path) as connection:
            row = connection.execute("SELECT payload_json FROM plans WHERE plan_id = ?", (plan_id,)).fetchone()
        if row is None:
            raise ContractError("plan_id was not found in persistent plan store.")
        payload = json.loads(str(row[0]))
        if not isinstance(payload, dict):
            raise ContractError("stored plan payload is invalid.")
        return payload

    def request_cancel(self, plan_id: str, reason: str, requested_by: str = "operator") -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        detail = f"{requested_by}: {reason.strip()}" if reason.strip() else requested_by
        with sqlite3.connect(self.sqlite_path) as connection:
            connection.execute(
                "INSERT INTO cancellations (plan_id, requested, reason, requested_at) VALUES (?, 1, ?, ?) ON CONFLICT(plan_id) DO UPDATE SET requested = 1, reason = excluded.reason, requested_at = excluded.requested_at",
                (plan_id, detail, now),
            )
        return {"plan_id": plan_id, "cancel_requested": True, "reason": detail, "requested_at": now}

    def is_cancel_requested(self, plan_id: str) -> bool:
        with sqlite3.connect(self.sqlite_path) as connection:
            row = connection.execute("SELECT requested FROM cancellations WHERE plan_id = ?", (plan_id,)).fetchone()
        return bool(row and int(row[0]) == 1)

    def mark_status(self, plan_id: str, status: str) -> None:
        now = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.sqlite_path) as connection:
            row = connection.execute("SELECT payload_json FROM plans WHERE plan_id = ?", (plan_id,)).fetchone()
            payload_json = None
            if row is not None:
                payload = json.loads(str(row[0]))
                if isinstance(payload, dict):
                    payload["status"] = status
                    payload_json = json.dumps(payload, sort_keys=True, ensure_ascii=False)
            if payload_json is None:
                connection.execute("UPDATE plans SET status = ?, updated_at = ? WHERE plan_id = ?", (status, now, plan_id))
            else:
                connection.execute("UPDATE plans SET status = ?, payload_json = ?, updated_at = ? WHERE plan_id = ?", (status, payload_json, now, plan_id))


class AliasTechniqueWorker(BaseWorker):
    """Worker adapter for the class-style worker names used by module manifests."""

    worker_name = "m12_alias_worker"

    def __init__(self, aliases: set[str]) -> None:
        self.aliases = set(aliases)

    def can_handle(self, worker_name: str) -> bool:
        return worker_name in self.aliases


def _normalize_modules(requested_modules: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    modules = tuple(dict.fromkeys(requested_modules or M12_ALLOWED_MODULES))
    invalid = [module_id for module_id in modules if module_id not in M12_ALLOWED_MODULES]
    if invalid:
        raise ContractError(f"M12 can only orchestrate implemented allowed modules: {', '.join(invalid)}")
    return modules


def _target_with_modules(target: TargetRecord, modules: tuple[str, ...]) -> TargetRecord:
    return TargetRecord(
        target_id=target.target_id,
        name=target.name,
        target_type=target.target_type,
        value=target.value,
        normalized_value=target.normalized_value,
        mode=target.mode,
        allowed_modules=[module for module in modules if module in M12_EXECUTABLE_MODULES],
        limits=dict(target.limits),
        noise_profile=target.noise_profile,
        evidence_profile=target.evidence_profile,
        require_confirmations=target.require_confirmations,
        metadata=dict(target.metadata),
        created_by=target.created_by,
        created_at=target.created_at,
    )


def build_m12_orchestration_plan(
    target: TargetRecord,
    registry: TechniqueRegistry,
    requested_modules: list[str] | tuple[str, ...] | None = None,
    confirmed: bool = False,
    allowlisted_target: bool = True,
    hardware_available: bool = True,
    network_available: bool = True,
    user_logic_available: bool = False,
    plan_id: str | None = None,
    m16_readiness: dict[str, Any] | None = None,
) -> M12OrchestrationPlan:
    """Build an auditable M12 plan without executing module techniques."""
    modules = _normalize_modules(requested_modules)
    readiness = m16_readiness if m16_readiness is not None else build_m16_readiness_report()
    strategy = OjoRouter(registry).plan_target(
        target=_target_with_modules(target, modules),
        confirmed=confirmed,
        allowlisted_target=allowlisted_target,
        hardware_available=hardware_available,
        network_available=network_available,
        user_logic_available=user_logic_available,
    )
    steps: list[M12PlanStep] = []
    for step in strategy.steps:
        technique = registry.require(step.technique_id)()
        steps.append(
            M12PlanStep(
                step=len(steps) + 1,
                technique_id=step.technique_id,
                module_id=step.module_id,
                worker=technique.worker,
                can_run_now=step.can_run_now,
                blocked_reason=step.blocked_reason,
                reason=step.reason,
                expected_evidence=tuple(step.expected_evidence),
                required_inputs=tuple(step.required_inputs),
                missing_inputs=tuple(step.missing_inputs),
            )
        )
    return M12OrchestrationPlan(
        plan_id=plan_id or f"m12-plan-{uuid4()}",
        target_id=target.target_id,
        mode=target.mode,
        requested_modules=modules,
        status=strategy.status,
        steps=tuple(steps),
        m16_readiness={
            "status": readiness.get("status"),
            "check_count": len(readiness.get("checks", [])) if isinstance(readiness.get("checks", []), list) else 0,
            "execution_implied": False,
        },
        execution_implied=False,
    )


def _default_m12_workers() -> list[BaseWorker]:
    aliases = set(M12_WORKER_ALIASES) | set(M12_WORKER_ALIASES.values())
    return [AliasTechniqueWorker(aliases)]


def run_m12_orchestration_plan(
    plan: M12OrchestrationPlan,
    registry: TechniqueRegistry,
    parameters_by_technique: dict[str, dict[str, Any]] | None = None,
    created_by: str = "m12_orchestrator",
    kill_switch: KillSwitchController | None = None,
    evidence_store: object | None = None,
    scoring_engine: object | None = None,
    workers: list[BaseWorker] | None = None,
    plan_store: M12PersistentPlanStore | None = None,
    retry_policy: dict[str, int] | None = None,
    step_dependencies: dict[str, dict[str, Any]] | None = None,
) -> M12RunSummary:
    """Execute runnable allowed plan steps through JobRunner one technique at a time."""
    parameters_by_technique = parameters_by_technique or {}
    retry_policy = retry_policy or {}
    step_dependencies = step_dependencies or {}
    runner = JobRunner(
        registry=registry,
        workers=workers if workers is not None else _default_m12_workers(),
        kill_switch=kill_switch if kill_switch is not None else get_global_kill_switch(),
        evidence_store=evidence_store,
    )
    if plan_store is not None:
        plan_store.save_plan(plan)
    results: list[JobResult] = []
    result_by_technique: dict[str, JobResult] = {}
    step_attempts: list[dict[str, Any]] = []
    canceled = False
    for step in plan.runnable_steps:
        if plan_store is not None and plan_store.is_cancel_requested(plan.plan_id):
            canceled = True
            break
        if step.module_id not in M12_EXECUTABLE_MODULES:
            continue
        dependency = step_dependencies.get(step.technique_id, {})
        depends_on = str(dependency.get("depends_on", "")).strip()
        required_status = str(dependency.get("required_status", JOB_STATUS_SUCCESS)).strip()
        if depends_on:
            dependency_result = result_by_technique.get(depends_on)
            if dependency_result is None or dependency_result.status != required_status:
                skipped = JobResult(
                    job_id=f"{plan.plan_id}-step-{step.step}",
                    status="stopped",
                    result_status=RESULT_SKIPPED,
                    summary=f"Step skipped because dependency {depends_on} did not reach {required_status}.",
                    error="dependency_not_satisfied",
                )
                results.append(skipped)
                result_by_technique[step.technique_id] = skipped
                step_attempts.append({"technique_id": step.technique_id, "attempt": 0, "status": "skipped", "dependency": depends_on})
                continue
        max_attempts = max(1, int(retry_policy.get(step.technique_id, 1)))
        last_result: JobResult | None = None
        for attempt in range(1, max_attempts + 1):
            request = JobRequest(
                job_id=f"{plan.plan_id}-step-{step.step}" if max_attempts == 1 else f"{plan.plan_id}-step-{step.step}-attempt-{attempt}",
                target_id=plan.target_id,
                created_by=created_by,
                mode=plan.mode,
                selected_modules=[step.module_id],
                selected_techniques=[step.technique_id],
                permissions_snapshot={
                    "confirmed": True,
                    "parameters": dict(parameters_by_technique.get(step.technique_id, {})),
                    "orchestrated_by": M12_MODULE_ID,
                    "attempt": attempt,
                },
            )
            last_result = runner.run_job(request)
            step_attempts.append({"technique_id": step.technique_id, "attempt": attempt, "status": last_result.status, "result_status": last_result.result_status})
            if last_result.status == JOB_STATUS_SUCCESS:
                break
            if plan_store is not None and plan_store.is_cancel_requested(plan.plan_id):
                canceled = True
                break
        if last_result is not None:
            results.append(last_result)
            result_by_technique[step.technique_id] = last_result
        if canceled:
            break
    scoring_updates: list[dict[str, Any]] = []
    for step, result in zip(plan.runnable_steps, results, strict=False):
        if scoring_engine is None:
            continue
        update_after_result = getattr(scoring_engine, "update_after_result", None)
        if not callable(update_after_result):
            raise ContractError("scoring_engine must expose update_after_result(event).")
        update = update_after_result(
            ScoringEvent(
                target_id=plan.target_id,
                technique_id=step.technique_id,
                module_id=step.module_id,
                run_id=result.job_id,
                result_status=result.result_status,
                evidence_quality=EVIDENCE_QUALITY_MEDIUM if result.evidence_ids else "none",
                evidence_ids=list(result.evidence_ids),
                demo=plan.mode == "demo",
                real_execution=plan.mode != "demo",
            )
        )
        if isinstance(update, dict):
            scoring_updates.append(dict(update))
        else:
            to_dict = getattr(update, "to_dict", None)
            scoring_updates.append(to_dict() if callable(to_dict) else dict(getattr(update, "__dict__", {})))
    evidence_ids = tuple(evidence_id for result in results for evidence_id in result.evidence_ids)
    if canceled:
        status = "canceled"
    elif not results:
        status = JOB_STATUS_FAILED
    elif all(result.status == JOB_STATUS_SUCCESS for result in results):
        status = JOB_STATUS_SUCCESS
    elif any(result.status == JOB_STATUS_SUCCESS for result in results):
        status = JOB_STATUS_PARTIAL
    else:
        status = JOB_STATUS_FAILED
    if plan_store is not None:
        plan_store.mark_status(plan.plan_id, status)
    return M12RunSummary(
        plan_id=plan.plan_id,
        target_id=plan.target_id,
        status=status,
        job_results=tuple(results),
        evidence_ids=evidence_ids,
        execution_performed=bool(results),
        scoring_updates=tuple(scoring_updates),
        canceled=canceled,
        step_attempts=tuple(step_attempts),
    )


@dataclass(frozen=True, slots=True)
class M12TimelineEvent:
    """One ordered M12 execution timeline event."""

    event_index: int
    event_type: str
    plan_id: str
    target_id: str
    technique_id: str | None
    step: int | None
    status: str
    detail: str
    job_id: str | None = None
    evidence_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_index": self.event_index,
            "event_type": self.event_type,
            "plan_id": self.plan_id,
            "target_id": self.target_id,
            "technique_id": self.technique_id,
            "step": self.step,
            "status": self.status,
            "detail": self.detail,
            "job_id": self.job_id,
            "evidence_ids": list(self.evidence_ids),
        }


def build_m12_execution_timeline(plan: M12OrchestrationPlan, summary: M12RunSummary) -> dict[str, Any]:
    """Build a deterministic timeline view from a plan and run summary."""
    events: list[M12TimelineEvent] = [
        M12TimelineEvent(
            event_index=1,
            event_type="plan_created",
            plan_id=plan.plan_id,
            target_id=plan.target_id,
            technique_id=None,
            step=None,
            status=plan.status,
            detail=f"Plan contains {len(plan.steps)} step(s), {len(plan.runnable_steps)} runnable.",
        )
    ]
    index = 2
    step_by_technique = {step.technique_id: step.step for step in plan.steps}
    for attempt in summary.step_attempts:
        technique_id = str(attempt.get("technique_id") or "")
        status = str(attempt.get("status") or "unknown")
        event_type = "step_skipped" if status == "skipped" else "step_attempt"
        detail = f"attempt={attempt.get('attempt')} status={status}"
        if attempt.get("dependency"):
            detail += f" dependency={attempt['dependency']}"
        events.append(
            M12TimelineEvent(
                event_index=index,
                event_type=event_type,
                plan_id=plan.plan_id,
                target_id=plan.target_id,
                technique_id=technique_id or None,
                step=step_by_technique.get(technique_id),
                status=status,
                detail=detail,
            )
        )
        index += 1
    for result in summary.job_results:
        technique_id = None
        if result.job_id.startswith(plan.plan_id):
            for step in plan.steps:
                if f"step-{step.step}" in result.job_id:
                    technique_id = step.technique_id
                    break
        events.append(
            M12TimelineEvent(
                event_index=index,
                event_type="job_result",
                plan_id=plan.plan_id,
                target_id=plan.target_id,
                technique_id=technique_id,
                step=step_by_technique.get(technique_id or ""),
                status=result.status,
                detail=result.summary or result.error or "Job completed.",
                job_id=result.job_id,
                evidence_ids=tuple(result.evidence_ids),
            )
        )
        index += 1
    events.append(
        M12TimelineEvent(
            event_index=index,
            event_type="run_completed",
            plan_id=plan.plan_id,
            target_id=plan.target_id,
            technique_id=None,
            step=None,
            status=summary.status,
            detail="Run canceled." if summary.canceled else "Run completed.",
            evidence_ids=summary.evidence_ids,
        )
    )
    return {
        "plan_id": plan.plan_id,
        "target_id": plan.target_id,
        "status": summary.status,
        "event_count": len(events),
        "events": [event.to_dict() for event in events],
    }


class OrchestrationPlanTechnique(BaseTechnique):
    """Prepare an M12 plan across implemented modules without execution."""

    technique_id = "orchestration.x5.plan_allowed_modules"
    module_id = M12_MODULE_ID
    display_name = "M12 X5 allowed-module planner"
    description = "Build a policy-checked plan for M01, M03, M09 and M16 readiness without executing attack modules."
    tool_name = "OjoRouter"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["target_profile"]
    optional_inputs = ["requested_modules", "confirmed", "allowlisted_target"]
    expected_evidence = ["orchestration_plan", "m16_readiness_summary", "normalized_json"]
    input_schema = {"target_profile": {"type": "object"}, "requested_modules": {"type": "array"}}
    ai_fillable_inputs = ["requested_modules"]
    panel_fields = [{"name": "target_profile", "label": "Target profile", "type": "textarea"}]
    success_markers = ["orchestration_plan"]
    failure_markers = ["invalid_module", "invalid_target"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"orchestration_plan": "dict"}
    version_lock_id = "m12_orchestration/x5-plan-allowed-modules"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        from app.core.runtime_registry import get_runtime_registry

        profile = context.parameters.get("target_profile")
        if not isinstance(profile, dict):
            raise ContractError("target_profile must be an object.")
        target = TargetRecord(
            target_id=str(profile.get("target_id") or context.target_id),
            name=str(profile.get("name") or profile.get("target_id") or context.target_id),
            target_type=str(profile.get("target_type") or "custom"),
            value=str(profile.get("value") or profile.get("normalized_value") or context.target_id),
            normalized_value=str(profile.get("normalized_value") or profile.get("value") or context.target_id),
            mode=str(profile.get("mode") or context.mode),
            metadata=dict(profile.get("metadata", {})) if isinstance(profile.get("metadata", {}), dict) else {},
        )
        requested_modules = context.parameters.get("requested_modules")
        if requested_modules is not None and not isinstance(requested_modules, list):
            raise ContractError("requested_modules must be a list when provided.")
        plan = build_m12_orchestration_plan(
            target=target,
            registry=get_runtime_registry(),
            requested_modules=requested_modules,
            confirmed=bool(context.parameters.get("confirmed", context.confirmed)),
            allowlisted_target=bool(context.parameters.get("allowlisted_target", True)),
        )
        content = {"orchestration_plan": plan.to_dict(), "m16_readiness_summary": plan.m16_readiness, "execution_implied": False}
        evidence = EvidenceRecord(
            evidence_id=f"ev-{uuid4()}",
            run_id=context.run_id,
            target_id=context.target_id,
            technique_id=self.technique_id,
            module_id=M12_MODULE_ID,
            evidence_type="orchestration_plan",
            quality=EVIDENCE_QUALITY_MEDIUM,
            summary="M12 built a non-executing orchestration plan.",
            content=content,
            source="m12-orchestrator",
            demo=False,
            real_execution=True,
        )
        return TechniqueExecutionResult(self.technique_id, M12_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)
