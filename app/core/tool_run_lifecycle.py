"""Lifecycle updates for prepared tool-run workspaces."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from app.core.workspace import load_tool_run_manifest, normalize_run_id, normalize_tool_id, tool_run_workspace_for_module

ToolRunStatus = Literal["prepared", "running", "completed", "failed", "cancelled"]
_ALLOWED_STATUS_TRANSITIONS: dict[ToolRunStatus, set[ToolRunStatus]] = {
    "prepared": {"running", "completed", "failed", "cancelled"},
    "running": {"completed", "failed", "cancelled"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
}
_TERMINAL_STATUSES: set[ToolRunStatus] = {"completed", "failed", "cancelled"}


@dataclass(frozen=True, slots=True)
class ToolRunLifecycleUpdate:
    """Result of a persisted tool-run lifecycle update."""

    module_id: str
    tool_id: str
    run_id: str
    previous_status: ToolRunStatus
    status: ToolRunStatus
    manifest_path: Path
    manifest: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "module_id": self.module_id,
            "tool_id": self.tool_id,
            "run_id": self.run_id,
            "previous_status": self.previous_status,
            "status": self.status,
            "manifest_path": self.manifest_path.as_posix(),
            "manifest": self.manifest,
        }


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _coerce_status(value: object) -> ToolRunStatus:
    if value not in _ALLOWED_STATUS_TRANSITIONS:
        raise ValueError(f"Unsupported tool-run status: {value!r}.")
    return value  # type: ignore[return-value]


def update_tool_run_status(
    module_id: str,
    tool_id: str,
    run_id: str,
    status: ToolRunStatus,
    note: str | None = None,
    repo_root: Path | None = None,
) -> ToolRunLifecycleUpdate:
    """Persist a lifecycle status update into an existing tool-run manifest."""
    normalized_tool_id = normalize_tool_id(tool_id)
    normalized_run_id = normalize_run_id(run_id)
    manifest = load_tool_run_manifest(module_id, normalized_tool_id, normalized_run_id, repo_root=repo_root)
    previous_status = _coerce_status(manifest.get("status"))
    if status == previous_status:
        next_manifest = dict(manifest)
    elif status not in _ALLOWED_STATUS_TRANSITIONS[previous_status]:
        raise ValueError(f"Cannot transition tool run from {previous_status!r} to {status!r}.")
    else:
        next_manifest = dict(manifest)
        next_manifest["status"] = status
    now = _utc_now_iso()
    next_manifest["updated_at"] = now
    if status == "running" and "started_at" not in next_manifest:
        next_manifest["started_at"] = now
    if status in _TERMINAL_STATUSES and "finished_at" not in next_manifest:
        next_manifest["finished_at"] = now
    if note is not None:
        next_manifest["status_note"] = note.strip()[:500]

    run_workspace = tool_run_workspace_for_module(module_id, normalized_tool_id, normalized_run_id, repo_root=repo_root)
    run_workspace.manifest_path.write_text(
        json.dumps(next_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return ToolRunLifecycleUpdate(
        module_id=str(next_manifest["module_id"]),
        tool_id=normalized_tool_id,
        run_id=normalized_run_id,
        previous_status=previous_status,
        status=status,
        manifest_path=run_workspace.manifest_path,
        manifest=next_manifest,
    )
