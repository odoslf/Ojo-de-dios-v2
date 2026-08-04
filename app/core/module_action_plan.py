"""Generic action plans and progress boards for target-scoped module findings."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.module_findings import TargetModuleFinding, derive_target_module_findings
from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M01_MODULE_ID = "m01_osint"
VALID_MODULE_ACTION_STATUSES = frozenset({"pending", "in_progress", "completed", "dismissed"})
_PRIORITY_BY_SEVERITY = {
    "critical": "high",
    "high": "high",
    "medium": "medium",
    "low": "low",
    "info": "info",
}
_PRIORITY_SORT = {"high": 0, "medium": 1, "low": 2, "info": 3, "review": 4}


@dataclass(frozen=True, slots=True)
class ModuleActionStep:
    """One deterministic operator action derived from persisted module evidence."""

    step_id: str
    module_id: str
    finding_id: str | None
    priority: str
    action_type: str
    title: str
    instruction: str
    evidence_refs: tuple[str, ...]
    source: str

    def to_dict(self) -> dict[str, object]:
        return {
            "step_id": self.step_id,
            "module_id": self.module_id,
            "finding_id": self.finding_id,
            "priority": self.priority,
            "action_type": self.action_type,
            "title": self.title,
            "instruction": self.instruction,
            "evidence_refs": list(self.evidence_refs),
            "source": self.source,
            "target_activity_performed": False,
        }


@dataclass(frozen=True, slots=True)
class ModuleActionPlan:
    """A module-scoped operator plan built from real stored evidence findings."""

    target_id: str
    module_id: str
    generated_at: str
    steps: tuple[ModuleActionStep, ...]
    source_finding_count: int
    source_artifact_count: int
    source_review_count: int
    source_stored_evidence_count: int
    unverified_stored_evidence_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "plan_type": "target_module_operator_action_plan",
            "target_id": self.target_id,
            "module_id": self.module_id,
            "generated_at": self.generated_at,
            "step_count": len(self.steps),
            "source_finding_count": self.source_finding_count,
            "source_artifact_count": self.source_artifact_count,
            "source_review_count": self.source_review_count,
            "source_stored_evidence_count": self.source_stored_evidence_count,
            "unverified_stored_evidence_count": self.unverified_stored_evidence_count,
            "steps": [step.to_dict() for step in self.steps],
            "target_activity_performed": False,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _step_id(target_id: str, module_id: str, finding_id: str | None, action_type: str, instruction: str) -> str:
    material = "|".join((target_id, module_id, finding_id or "", action_type, instruction))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def _validate_module_id(module_id: str) -> str:
    clean = module_id.strip()
    if clean == M01_MODULE_ID:
        raise ValueError("M01 has a dedicated action plan endpoint; use /m01/action-plan.")
    return clean


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _artifact_payloads(target: TargetRecord, module_id: str, repo_root: Path | None) -> tuple[tuple[Path, dict[str, Any]], ...]:
    binding = bind_target_module_workspace(target, module_id, repo_root=repo_root)
    artifacts: list[tuple[Path, dict[str, Any]]] = []
    for directory_name in ("evidence", "outputs"):
        directory = binding.root_path / directory_name
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.json")):
            payload = _read_json_object(path)
            if payload is not None:
                artifacts.append((path, payload))
    return tuple(artifacts)


def _finding_dict(finding: TargetModuleFinding | dict[str, Any]) -> dict[str, Any]:
    return finding.to_dict() if isinstance(finding, TargetModuleFinding) else dict(finding)


def _action_type_for(priority: str) -> str:
    if priority == "high":
        return "review_prioritise_and_contain"
    if priority == "medium":
        return "validate_and_schedule"
    if priority == "low":
        return "triage_and_enrich"
    if priority == "info":
        return "preserve_and_correlate"
    return "collect_module_evidence"


def _step_from_finding(
    target: TargetRecord,
    module_id: str,
    finding: TargetModuleFinding | dict[str, Any],
    artifact_ref: str | None = None,
) -> ModuleActionStep:
    item = _finding_dict(finding)
    severity = str(item.get("severity") or "review").casefold()
    priority = _PRIORITY_BY_SEVERITY.get(severity, "review")
    finding_id = str(item.get("finding_id") or "").strip() or None
    recommendation = str(item.get("recommendation") or "").strip()
    instruction = recommendation or "Review the persisted module evidence and decide the next authorised operator action."
    raw_refs = item.get("evidence_refs", [])
    refs = [str(ref) for ref in raw_refs if ref] if isinstance(raw_refs, list) else []
    if artifact_ref and artifact_ref not in refs:
        refs.append(artifact_ref)
    action_type = _action_type_for(priority)
    return ModuleActionStep(
        step_id=_step_id(target.target_id, module_id, finding_id, action_type, instruction),
        module_id=module_id,
        finding_id=finding_id,
        priority=priority,
        action_type=action_type,
        title=str(item.get("title") or "Review module evidence"),
        instruction=instruction,
        evidence_refs=tuple(refs),
        source="module_finding",
    )


def _step_from_review_recommendation(
    target: TargetRecord,
    module_id: str,
    review_id: str,
    recommendation: str,
    index: int,
) -> ModuleActionStep:
    instruction = recommendation.strip()
    title = instruction[:96].rstrip(".") if instruction else "Review local AI recommendation"
    evidence_ref = f"ai_review:{review_id}:recommended_next_steps:{index}"
    return ModuleActionStep(
        step_id=_step_id(target.target_id, module_id, review_id, "review_laia_recommendation", instruction),
        module_id=module_id,
        finding_id=None,
        priority="review",
        action_type="review_laia_recommendation",
        title=title,
        instruction=instruction,
        evidence_refs=(evidence_ref,),
        source="local_ai_review",
    )


def _review_recommendation_steps(
    target: TargetRecord,
    module_id: str,
    repo_root: Path | None,
    limit: int = 5,
) -> tuple[ModuleActionStep, ...]:
    from app.ai.module_context import list_target_module_ai_reviews

    steps: list[ModuleActionStep] = []
    for review in list_target_module_ai_reviews(target, module_id, repo_root=repo_root, limit=limit):
        parsed = review.get("parsed_content")
        if not isinstance(parsed, dict):
            continue
        raw_recommendations = parsed.get("recommended_next_steps", [])
        recommendations = raw_recommendations if isinstance(raw_recommendations, list) else []
        review_id = str(review.get("review_id") or "unknown")
        for index, recommendation in enumerate(recommendations):
            clean = str(recommendation).strip()
            if clean:
                steps.append(_step_from_review_recommendation(target, module_id, review_id, clean, index))
    return tuple(steps)


def _fallback_step(target: TargetRecord, module_id: str) -> ModuleActionStep:
    instruction = "Import or generate module evidence, then re-open this plan so findings can drive concrete actions."
    return ModuleActionStep(
        step_id=_step_id(target.target_id, module_id, None, "collect_module_evidence", instruction),
        module_id=module_id,
        finding_id=None,
        priority="review",
        action_type="collect_module_evidence",
        title="No module findings available yet",
        instruction=instruction,
        evidence_refs=(),
        source="missing_module_findings",
    )


def build_module_action_plan(
    target: TargetRecord,
    module_id: str,
    findings: list[dict[str, Any]] | tuple[TargetModuleFinding, ...] | None = None,
    repo_root: Path | None = None,
    include_reviews: bool = True,
    extra_findings: list[dict[str, Any]] | tuple[TargetModuleFinding, ...] | None = None,
    source_stored_evidence_count: int = 0,
    unverified_stored_evidence_count: int = 0,
) -> ModuleActionPlan:
    """Build a deterministic action plan from module findings or persisted module artifacts."""
    clean_module_id = _validate_module_id(module_id)
    steps_by_id: dict[str, ModuleActionStep] = {}
    source_finding_count = 0
    source_artifact_count = 0
    source_review_count = 0
    if findings is not None:
        source_finding_count = len(findings)
        for finding in findings:
            step = _step_from_finding(target, clean_module_id, finding)
            steps_by_id.setdefault(step.step_id, step)
    else:
        artifacts = _artifact_payloads(target, clean_module_id, repo_root)
        source_artifact_count = len(artifacts)
        for path, payload in artifacts:
            derived = derive_target_module_findings(clean_module_id, payload)
            source_finding_count += len(derived)
            for finding in derived:
                step = _step_from_finding(target, clean_module_id, finding, artifact_ref=path.as_posix())
                steps_by_id.setdefault(step.step_id, step)
    if extra_findings:
        source_finding_count += len(extra_findings)
        for finding in extra_findings:
            step = _step_from_finding(target, clean_module_id, finding)
            steps_by_id.setdefault(step.step_id, step)
    if include_reviews:
        review_steps = _review_recommendation_steps(target, clean_module_id, repo_root)
        source_review_count = len(review_steps)
        for step in review_steps:
            steps_by_id.setdefault(step.step_id, step)
    if not steps_by_id:
        fallback = _fallback_step(target, clean_module_id)
        steps_by_id[fallback.step_id] = fallback
    steps = tuple(sorted(steps_by_id.values(), key=lambda item: (_PRIORITY_SORT.get(item.priority, 9), item.title, item.step_id)))
    return ModuleActionPlan(
        target_id=target.target_id,
        module_id=clean_module_id,
        generated_at=_now(),
        steps=steps,
        source_finding_count=source_finding_count,
        source_artifact_count=source_artifact_count,
        source_review_count=source_review_count,
        source_stored_evidence_count=max(int(source_stored_evidence_count), 0),
        unverified_stored_evidence_count=max(int(unverified_stored_evidence_count), 0),
    )


def _action_plan_path(target: TargetRecord, module_id: str, repo_root: Path | None) -> Path:
    binding = bind_target_module_workspace(target, module_id, repo_root=repo_root)
    return binding.root_path / "action_plans" / "current.json"


def _progress_path(target: TargetRecord, module_id: str, repo_root: Path | None) -> Path:
    binding = bind_target_module_workspace(target, module_id, repo_root=repo_root)
    return binding.root_path / "action_plans" / "progress.json"


def write_module_action_plan(
    target: TargetRecord,
    module_id: str,
    repo_root: Path | None = None,
    extra_findings: list[dict[str, Any]] | tuple[TargetModuleFinding, ...] | None = None,
    source_stored_evidence_count: int = 0,
    unverified_stored_evidence_count: int = 0,
) -> Path:
    """Persist the current module action plan and return its path."""
    plan = build_module_action_plan(
        target,
        module_id,
        repo_root=repo_root,
        extra_findings=extra_findings,
        source_stored_evidence_count=source_stored_evidence_count,
        unverified_stored_evidence_count=unverified_stored_evidence_count,
    )
    path = _action_plan_path(target, plan.module_id, repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_module_action_plan(target: TargetRecord, module_id: str, repo_root: Path | None = None) -> dict[str, Any] | None:
    """Read the persisted module action plan if one exists."""
    clean_module_id = _validate_module_id(module_id)
    return _read_json_object(_action_plan_path(target, clean_module_id, repo_root))


def _load_progress(path: Path) -> dict[str, dict[str, Any]]:
    payload = _read_json_object(path)
    events = payload.get("events", []) if isinstance(payload, dict) else []
    latest: dict[str, dict[str, Any]] = {}
    if not isinstance(events, list):
        return latest
    for event in events:
        if not isinstance(event, dict):
            continue
        step_id = str(event.get("step_id") or "").strip()
        status = str(event.get("status") or "")
        if step_id and status in VALID_MODULE_ACTION_STATUSES:
            latest[step_id] = event
    return latest


def _progress_events(path: Path) -> list[dict[str, Any]]:
    payload = _read_json_object(path)
    events = payload.get("events", []) if isinstance(payload, dict) else []
    return [event for event in events if isinstance(event, dict)] if isinstance(events, list) else []


def build_module_action_board(
    target: TargetRecord,
    module_id: str,
    repo_root: Path | None = None,
    extra_findings: list[dict[str, Any]] | tuple[TargetModuleFinding, ...] | None = None,
    source_stored_evidence_count: int = 0,
    unverified_stored_evidence_count: int = 0,
) -> dict[str, object]:
    """Merge the current module plan with persisted operator progress."""
    plan = build_module_action_plan(
        target,
        module_id,
        repo_root=repo_root,
        extra_findings=extra_findings,
        source_stored_evidence_count=source_stored_evidence_count,
        unverified_stored_evidence_count=unverified_stored_evidence_count,
    )
    latest_progress = _load_progress(_progress_path(target, plan.module_id, repo_root))
    steps: list[dict[str, object]] = []
    for step in plan.steps:
        progress = latest_progress.get(step.step_id)
        item = step.to_dict()
        item["progress"] = progress or {
            "step_id": step.step_id,
            "status": "pending",
            "note": "",
            "updated_at": None,
            "target_activity_performed": False,
        }
        steps.append(item)
    return {
        "board_type": "target_module_operator_action_board",
        "target_id": target.target_id,
        "module_id": plan.module_id,
        "generated_at": _now(),
        "plan": plan.to_dict(),
        "steps": steps,
        "open_count": sum(1 for item in steps if item["progress"]["status"] in {"pending", "in_progress"}),
        "completed_count": sum(1 for item in steps if item["progress"]["status"] == "completed"),
        "target_activity_performed": False,
    }


def update_module_action_progress(
    target: TargetRecord,
    module_id: str,
    step_id: str,
    status: str,
    note: str = "",
    repo_root: Path | None = None,
    extra_findings: list[dict[str, Any]] | tuple[TargetModuleFinding, ...] | None = None,
    source_stored_evidence_count: int = 0,
    unverified_stored_evidence_count: int = 0,
) -> dict[str, object]:
    """Record an operator-only progress update for a module action step."""
    clean_status = status.strip()
    if clean_status not in VALID_MODULE_ACTION_STATUSES:
        raise ValueError(f"Invalid module action status: {status}.")
    clean_note = note.strip()
    if clean_status in {"completed", "dismissed"} and not clean_note:
        raise ValueError("A note is required when completing or dismissing a module action.")
    board = build_module_action_board(
        target,
        module_id,
        repo_root=repo_root,
        extra_findings=extra_findings,
        source_stored_evidence_count=source_stored_evidence_count,
        unverified_stored_evidence_count=unverified_stored_evidence_count,
    )
    known_steps = {str(item["step_id"]) for item in board["steps"]}
    if step_id not in known_steps:
        raise ValueError("The action step is not present in the current module evidence plan.")
    timestamp = _now()
    event = {
        "step_id": step_id,
        "status": clean_status,
        "note": clean_note,
        "updated_at": timestamp,
        "target_activity_performed": False,
    }
    path = _progress_path(target, str(board["module_id"]), repo_root)
    events = _progress_events(path)
    events.append(event)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "target_id": target.target_id,
                "module_id": board["module_id"],
                "events": events,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return build_module_action_board(
        target,
        str(board["module_id"]),
        repo_root=repo_root,
        extra_findings=extra_findings,
        source_stored_evidence_count=source_stored_evidence_count,
        unverified_stored_evidence_count=unverified_stored_evidence_count,
    )
