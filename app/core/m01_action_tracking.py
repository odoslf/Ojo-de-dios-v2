"""Persistent, operator-confirmed progress tracking for M01 action plans."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.core.m01_action_plan import M01ActionPlan, build_m01_action_plan
from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M01_MODULE_ID = "m01_osint"
VALID_M01_ACTION_STATUSES = frozenset({"pending", "in_progress", "completed", "dismissed"})


@dataclass(frozen=True, slots=True)
class M01ActionProgress:
    """Current state and immutable operator event history for one plan step."""

    step_id: str
    status: str
    note: str
    updated_at: str
    events: tuple[dict[str, str], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "step_id": self.step_id,
            "status": self.status,
            "note": self.note,
            "updated_at": self.updated_at,
            "events": list(self.events),
            "target_activity_performed": False,
        }


def _progress_path(target: TargetRecord, repo_root: Path | None) -> Path:
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M01_MODULE_ID, repo_root=root)
    return binding.root_path / "action_plans" / "progress.json"


def _load_progress(path: Path) -> dict[str, M01ActionProgress]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    items = payload.get("steps", []) if isinstance(payload, dict) else []
    result: dict[str, M01ActionProgress] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        step_id = str(item.get("step_id", "")).strip()
        status = str(item.get("status", "pending"))
        if not step_id or status not in VALID_M01_ACTION_STATUSES:
            continue
        raw_events = item.get("events", [])
        events = tuple(event for event in raw_events if isinstance(event, dict)) if isinstance(raw_events, list) else ()
        result[step_id] = M01ActionProgress(
            step_id=step_id,
            status=status,
            note=str(item.get("note", "")),
            updated_at=str(item.get("updated_at", "")),
            events=events,
        )
    return result


def build_m01_action_board(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object]:
    """Merge the latest evidence-derived plan with persisted operator progress."""
    plan: M01ActionPlan = build_m01_action_plan(target, repo_root=repo_root)
    persisted = _load_progress(_progress_path(target, repo_root))
    steps: list[dict[str, object]] = []
    for step in plan.steps:
        progress = persisted.get(step.step_id)
        item = step.to_dict()
        item["progress"] = (progress.to_dict() if progress else {
            "step_id": step.step_id,
            "status": "pending",
            "note": "",
            "updated_at": None,
            "events": [],
            "target_activity_performed": False,
        })
        steps.append(item)
    return {
        "board_type": "m01_operator_action_board",
        "target_id": target.target_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plan": plan.to_dict(),
        "steps": steps,
        "open_count": sum(1 for item in steps if item["progress"]["status"] in {"pending", "in_progress"}),
        "completed_count": sum(1 for item in steps if item["progress"]["status"] == "completed"),
        "target_activity_performed": False,
    }


def update_m01_action_progress(
    target: TargetRecord,
    step_id: str,
    status: str,
    note: str = "",
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Record an operator-confirmed state change for a currently derived M01 action."""
    if status not in VALID_M01_ACTION_STATUSES:
        raise ValueError(f"Invalid M01 action status: {status}.")
    clean_note = note.strip()
    if status in {"completed", "dismissed"} and not clean_note:
        raise ValueError("A note is required when completing or dismissing an M01 action.")
    board = build_m01_action_board(target, repo_root=repo_root)
    known_steps = {str(item["step_id"]) for item in board["steps"]}
    if step_id not in known_steps:
        raise ValueError("The action step is not present in the current M01 evidence plan.")
    path = _progress_path(target, repo_root)
    stored = _load_progress(path)
    previous = stored.get(step_id)
    timestamp = datetime.now(timezone.utc).isoformat()
    event = {"status": status, "note": clean_note, "updated_at": timestamp}
    events = (*previous.events, event) if previous else (event,)
    stored[step_id] = M01ActionProgress(step_id, status, clean_note, timestamp, events)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema_version": 1, "target_id": target.target_id, "steps": [item.to_dict() for item in stored.values()]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return build_m01_action_board(target, repo_root=repo_root)
