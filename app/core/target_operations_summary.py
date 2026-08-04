"""Target-wide operational summary built from persisted module workspaces."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.module_action_plan import build_module_action_plan
from app.core.module_catalog import ModuleCatalogEntry, get_module_by_id
from app.core.module_findings import derive_target_module_findings
from app.core.target_model import TargetRecord
from app.core.target_osint import list_target_passive_dns_history
from app.core.target_workspace import target_module_workspace_for_record, target_workspace_for_record

_ARTIFACT_DIRS = frozenset({"evidence", "outputs", "reports"})
_FINDING_DIRS = frozenset({"evidence", "outputs"})
_OPEN_PROGRESS_STATUSES = frozenset({"pending", "in_progress"})
_CLOSED_PROGRESS_STATUSES = frozenset({"completed", "dismissed"})


@dataclass(frozen=True, slots=True)
class TargetModuleOperationsSummary:
    """Operational state for one target-module workspace."""

    module_id: str
    module_number: int
    display_name: str
    workspace_path: str
    workspace_exists: bool
    artifact_count: int
    json_artifact_count: int
    finding_count: int
    action_step_count: int
    open_action_count: int
    completed_action_count: int
    review_count: int
    latest_review_path: str | None
    status: str

    def to_dict(self) -> dict[str, object]:
        return {
            "module_id": self.module_id,
            "module_number": self.module_number,
            "display_name": self.display_name,
            "workspace_path": self.workspace_path,
            "workspace_exists": self.workspace_exists,
            "artifact_count": self.artifact_count,
            "json_artifact_count": self.json_artifact_count,
            "finding_count": self.finding_count,
            "action_step_count": self.action_step_count,
            "open_action_count": self.open_action_count,
            "completed_action_count": self.completed_action_count,
            "review_count": self.review_count,
            "latest_review_path": self.latest_review_path,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class TargetOperationsSummary:
    """Target-level rollup for local operator workflow state."""

    target_id: str
    generated_at: str
    workspace_path: str
    workspace_exists: bool
    m01_history_count: int
    modules: tuple[TargetModuleOperationsSummary, ...]

    def to_dict(self) -> dict[str, object]:
        modules = [module.to_dict() for module in self.modules]
        return {
            "summary_type": "target_operations_summary",
            "target_id": self.target_id,
            "generated_at": self.generated_at,
            "workspace_path": self.workspace_path,
            "workspace_exists": self.workspace_exists,
            "m01_history_count": self.m01_history_count,
            "module_count": len(modules),
            "artifact_count": sum(int(module["artifact_count"]) for module in modules),
            "finding_count": sum(int(module["finding_count"]) for module in modules),
            "open_action_count": sum(int(module["open_action_count"]) for module in modules),
            "completed_action_count": sum(int(module["completed_action_count"]) for module in modules),
            "review_count": sum(int(module["review_count"]) for module in modules),
            "modules": modules,
            "target_activity_performed": False,
        }


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _selected_modules(target: TargetRecord) -> tuple[ModuleCatalogEntry, ...]:
    modules: list[ModuleCatalogEntry] = []
    seen: set[str] = set()
    for module_id in target.allowed_modules:
        module = get_module_by_id(module_id)
        if module is None or not module.official or module.module_number == 1 or module.module_id in seen:
            continue
        seen.add(module.module_id)
        modules.append(module)
    return tuple(sorted(modules, key=lambda item: item.module_number))


def _workspace_files(root_path: Path) -> tuple[Path, ...]:
    if not root_path.is_dir():
        return ()
    files: list[Path] = []
    for directory_name in sorted(_ARTIFACT_DIRS):
        directory = root_path / directory_name
        if directory.is_dir():
            files.extend(path for path in directory.rglob("*") if path.is_file())
    return tuple(sorted(files))


def _module_findings(module_id: str, root_path: Path) -> tuple[dict[str, Any], ...]:
    findings_by_id: dict[str, dict[str, Any]] = {}
    if not root_path.is_dir():
        return ()
    for directory_name in sorted(_FINDING_DIRS):
        directory = root_path / directory_name
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.json")):
            payload = _read_json_object(path)
            if payload is None:
                continue
            for finding in derive_target_module_findings(module_id, payload):
                findings_by_id[finding.finding_id] = finding.to_dict()
    return tuple(findings_by_id.values())


def _latest_progress_by_step(progress_path: Path) -> dict[str, str]:
    payload = _read_json_object(progress_path)
    events = payload.get("events", []) if isinstance(payload, dict) else []
    latest: dict[str, str] = {}
    if not isinstance(events, list):
        return latest
    for event in events:
        if not isinstance(event, dict):
            continue
        step_id = str(event.get("step_id") or "").strip()
        status = str(event.get("status") or "").strip()
        if step_id and status:
            latest[step_id] = status
    return latest


def _review_rollup(root_path: Path) -> tuple[int, str | None]:
    reviews_dir = root_path / "ai_reviews" / "laia_mistral"
    if not reviews_dir.is_dir():
        return 0, None
    reviews = sorted(reviews_dir.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    latest = reviews[0].as_posix() if reviews else None
    return len(reviews), latest


def _module_status(artifact_count: int, finding_count: int, open_action_count: int, completed_action_count: int) -> str:
    if artifact_count == 0:
        return "needs_evidence"
    if finding_count and open_action_count:
        return "findings_need_action"
    if completed_action_count and not open_action_count:
        return "actions_completed"
    if finding_count:
        return "findings_reviewed"
    return "evidence_collected"


def build_target_operations_summary(target: TargetRecord, repo_root: Path | None = None) -> TargetOperationsSummary:
    """Build a side-effect-light target rollup from existing local workspaces."""
    root = Path.cwd() if repo_root is None else repo_root
    target_workspace = target_workspace_for_record(target, repo_root=root)
    module_summaries: list[TargetModuleOperationsSummary] = []
    for module in _selected_modules(target):
        binding = target_module_workspace_for_record(target, module.module_id, repo_root=root)
        artifact_files = _workspace_files(binding.root_path)
        findings = _module_findings(module.module_id, binding.root_path)
        plan = build_module_action_plan(target, module.module_id, findings=list(findings), repo_root=root, include_reviews=False)
        latest_progress = _latest_progress_by_step(binding.root_path / "action_plans" / "progress.json")
        open_actions = 0
        completed_actions = 0
        for step in plan.steps:
            status = latest_progress.get(step.step_id, "pending")
            if status in _OPEN_PROGRESS_STATUSES:
                open_actions += 1
            elif status in _CLOSED_PROGRESS_STATUSES:
                completed_actions += 1
        review_count, latest_review_path = _review_rollup(binding.root_path)
        module_summaries.append(
            TargetModuleOperationsSummary(
                module_id=module.module_id,
                module_number=module.module_number,
                display_name=module.display_name,
                workspace_path=binding.root_path.as_posix(),
                workspace_exists=binding.root_path.is_dir(),
                artifact_count=len(artifact_files),
                json_artifact_count=sum(1 for path in artifact_files if path.suffix.lower() == ".json"),
                finding_count=len(findings),
                action_step_count=len(plan.steps),
                open_action_count=open_actions,
                completed_action_count=completed_actions,
                review_count=review_count,
                latest_review_path=latest_review_path,
                status=_module_status(len(artifact_files), len(findings), open_actions, completed_actions),
            )
        )
    return TargetOperationsSummary(
        target_id=target.target_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        workspace_path=target_workspace.root_path.as_posix(),
        workspace_exists=target_workspace.root_path.is_dir(),
        m01_history_count=len(list_target_passive_dns_history(target, repo_root=root, limit=50)),
        modules=tuple(module_summaries),
    )
