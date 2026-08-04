"""Workspace persistence for non-executing tool installation plans."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.core.tool_install_plan import ModuleToolInstallPlan, build_module_tool_install_plan
from app.core.workspace import ensure_module_workspace, workspace_for_module
from app.core.module_catalog import require_module_by_id

INSTALL_PLAN_DIRNAME = "install"
INSTALL_PLAN_FILENAME = "tool_install_plan.json"
INSTALL_PLAN_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class PersistedToolInstallPlan:
    """Metadata for a module install plan persisted into its workspace."""

    module_id: str
    path: Path
    sha256: str
    byte_count: int
    plan: ModuleToolInstallPlan

    def to_dict(self) -> dict[str, object]:
        return {
            "module_id": self.module_id,
            "path": self.path.as_posix(),
            "sha256": self.sha256,
            "byte_count": self.byte_count,
            "plan": self.plan.to_dict(),
            "execution_performed": False,
        }


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _install_plan_path(module_id: str, repo_root: Path | None = None) -> Path:
    module = require_module_by_id(module_id)
    workspace = workspace_for_module(module, repo_root=repo_root)
    return workspace.root_path / INSTALL_PLAN_DIRNAME / INSTALL_PLAN_FILENAME


def _json_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _payload_for_plan(plan: ModuleToolInstallPlan, generated_at: str) -> dict[str, object]:
    return {
        "schema_version": INSTALL_PLAN_SCHEMA_VERSION,
        "generated_at": generated_at,
        "module_id": plan.module_id,
        "install_plan": plan.to_dict(),
        "execution_performed": False,
        "approval_required_before_execution": True,
    }


def prepare_module_tool_install_plan(
    module_id: str,
    repo_root: Path | None = None,
) -> PersistedToolInstallPlan:
    """Build and persist a module install plan without executing installers."""
    plan = build_module_tool_install_plan(module_id)
    ensure_module_workspace(plan.module_id, repo_root=repo_root)
    path = _install_plan_path(plan.module_id, repo_root=repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = _json_bytes(_payload_for_plan(plan, _utc_now_iso()))
    path.write_bytes(content)
    return PersistedToolInstallPlan(
        module_id=plan.module_id,
        path=path,
        sha256=hashlib.sha256(content).hexdigest(),
        byte_count=len(content),
        plan=plan,
    )


def read_prepared_module_tool_install_plan(
    module_id: str,
    repo_root: Path | None = None,
) -> tuple[PersistedToolInstallPlan, dict[str, object]]:
    """Read a previously persisted module install plan from its workspace."""
    path = _install_plan_path(module_id, repo_root=repo_root)
    content = path.read_bytes()
    payload = json.loads(content.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Persisted install plan must contain a JSON object.")
    plan = build_module_tool_install_plan(module_id)
    return (
        PersistedToolInstallPlan(
            module_id=plan.module_id,
            path=path,
            sha256=hashlib.sha256(content).hexdigest(),
            byte_count=len(content),
            plan=plan,
        ),
        payload,
    )
