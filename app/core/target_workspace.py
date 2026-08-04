"""Filesystem workspaces bound to persisted targets."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from app.core.module_catalog import get_module_by_id, require_module_by_id
from app.core.target_model import TargetRecord
from app.core.workspace import ensure_module_workspace, workspace_for_module

TARGET_WORKSPACE_MANIFEST_FILENAME = "target_workspace_manifest.json"
TARGET_MODULE_BINDING_MANIFEST_FILENAME = "target_module_binding_manifest.json"
TARGET_WORKSPACE_DIRS = (
    "context",
    "fingerprints",
    "plans",
    "modules",
    "evidence",
    "reports",
    "tmp",
)
TARGET_MODULE_WORKSPACE_DIRS = (
    "inputs",
    "outputs",
    "evidence",
    "reports",
    "tool_runs",
    "tmp",
)
_TARGET_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,120}$")


@dataclass(frozen=True, slots=True)
class TargetWorkspace:
    """Concrete filesystem workspace for one stored target."""

    target_id: str
    root_path: Path
    manifest_path: Path
    standard_dirs: tuple[Path, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "target_id": self.target_id,
            "root_path": self.root_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "standard_dirs": [path.as_posix() for path in self.standard_dirs],
        }


@dataclass(frozen=True, slots=True)
class TargetModuleWorkspaceBinding:
    """Per-target binding for one catalog module workspace."""

    target_id: str
    module_id: str
    root_path: Path
    manifest_path: Path
    module_workspace_path: Path
    standard_dirs: tuple[Path, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "target_id": self.target_id,
            "module_id": self.module_id,
            "root_path": self.root_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "module_workspace_path": self.module_workspace_path.as_posix(),
            "standard_dirs": [path.as_posix() for path in self.standard_dirs],
        }


@dataclass(frozen=True, slots=True)
class TargetWorkspaceState:
    """Inspectable state for a target workspace without creating files."""

    target_id: str
    root_path: Path
    manifest_path: Path
    workspace_exists: bool
    manifest_exists: bool
    bound_modules: tuple[str, ...]

    @property
    def bound_module_count(self) -> int:
        return len(self.bound_modules)

    def to_dict(self) -> dict[str, object]:
        return {
            "target_id": self.target_id,
            "root_path": self.root_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "workspace_exists": self.workspace_exists,
            "manifest_exists": self.manifest_exists,
            "bound_module_count": self.bound_module_count,
            "bound_modules": list(self.bound_modules),
        }


def _repo_path(repo_root: Path, relative_path: str) -> Path:
    root = repo_root.resolve()
    resolved = (root / relative_path).resolve()
    if root != resolved and root not in resolved.parents:
        raise ValueError(f"Target workspace path escapes repository root: {relative_path}.")
    return resolved


def validate_target_workspace_id(target_id: str) -> str:
    """Validate target ids before using them in filesystem paths."""
    if not target_id or not _TARGET_ID_PATTERN.fullmatch(target_id) or ".." in target_id:
        raise ValueError("Target id is not safe for workspace paths.")
    return target_id


def target_workspace_for_record(target: TargetRecord, repo_root: Path | None = None) -> TargetWorkspace:
    """Return target workspace paths without creating files."""
    root = Path.cwd() if repo_root is None else repo_root
    target_id = validate_target_workspace_id(target.target_id)
    workspace_root = _repo_path(root, f"storage/targets/{target_id}")
    return TargetWorkspace(
        target_id=target_id,
        root_path=workspace_root,
        manifest_path=workspace_root / TARGET_WORKSPACE_MANIFEST_FILENAME,
        standard_dirs=tuple(workspace_root / dirname for dirname in TARGET_WORKSPACE_DIRS),
    )


def build_target_workspace_manifest(target: TargetRecord) -> dict[str, object]:
    """Build a JSON-safe manifest for a target workspace."""
    return {
        "schema_version": 1,
        "target_id": validate_target_workspace_id(target.target_id),
        "target_type": target.target_type,
        "name": target.name,
        "normalized_value": target.normalized_value,
        "mode": target.mode,
        "allowed_modules": list(target.allowed_modules),
        "limits": dict(target.limits),
        "noise_profile": target.noise_profile,
        "evidence_profile": target.evidence_profile,
        "require_confirmations": target.require_confirmations,
        "standard_dirs": list(TARGET_WORKSPACE_DIRS),
        "execution_implied": False,
        "workspace_purpose": "target_bound_operator_workspace",
    }


def ensure_target_workspace(target: TargetRecord, repo_root: Path | None = None) -> TargetWorkspace:
    """Create a target workspace and persist its structural manifest."""
    workspace = target_workspace_for_record(target, repo_root=repo_root)
    workspace.root_path.mkdir(parents=True, exist_ok=True)
    for directory in workspace.standard_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    workspace.manifest_path.write_text(
        json.dumps(build_target_workspace_manifest(target), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return workspace


def load_target_workspace_manifest(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object]:
    """Load a target workspace manifest."""
    workspace = target_workspace_for_record(target, repo_root=repo_root)
    if not workspace.manifest_path.is_file():
        raise FileNotFoundError(f"Target workspace manifest missing for {target.target_id}.")
    loaded = json.loads(workspace.manifest_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Target workspace manifest must be a JSON object for {target.target_id}.")
    return loaded


def target_module_workspace_for_record(
    target: TargetRecord,
    module_id: str,
    repo_root: Path | None = None,
) -> TargetModuleWorkspaceBinding:
    """Return the per-target module binding paths without creating files."""
    module = require_module_by_id(module_id)
    target_workspace = target_workspace_for_record(target, repo_root=repo_root)
    module_workspace = workspace_for_module(module, repo_root=repo_root)
    root_path = target_workspace.root_path / "modules" / module.module_id
    return TargetModuleWorkspaceBinding(
        target_id=target_workspace.target_id,
        module_id=module.module_id,
        root_path=root_path,
        manifest_path=root_path / TARGET_MODULE_BINDING_MANIFEST_FILENAME,
        module_workspace_path=module_workspace.root_path,
        standard_dirs=tuple(root_path / dirname for dirname in TARGET_MODULE_WORKSPACE_DIRS),
    )


def build_target_module_binding_manifest(target: TargetRecord, module_id: str, repo_root: Path | None = None) -> dict[str, object]:
    """Build the manifest connecting one target to one catalog module."""
    module = require_module_by_id(module_id)
    module_workspace = workspace_for_module(module, repo_root=repo_root)
    return {
        "schema_version": 1,
        "target_id": validate_target_workspace_id(target.target_id),
        "module_id": module.module_id,
        "module_number": module.module_number,
        "target_type": target.target_type,
        "target_normalized_value": target.normalized_value,
        "target_mode": target.mode,
        "target_workspace_path": f"storage/targets/{target.target_id}",
        "module_workspace_path": module_workspace.root_path.as_posix(),
        "standard_dirs": list(TARGET_MODULE_WORKSPACE_DIRS),
        "execution_implied": False,
        "binding_purpose": "target_module_workspace",
    }


def bind_target_module_workspace(
    target: TargetRecord,
    module_id: str,
    repo_root: Path | None = None,
) -> TargetModuleWorkspaceBinding:
    """Create a per-target module binding and ensure the global module workspace exists."""
    ensure_target_workspace(target, repo_root=repo_root)
    ensure_module_workspace(module_id, repo_root=repo_root)
    binding = target_module_workspace_for_record(target, module_id, repo_root=repo_root)
    binding.root_path.mkdir(parents=True, exist_ok=True)
    for directory in binding.standard_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    binding.manifest_path.write_text(
        json.dumps(build_target_module_binding_manifest(target, module_id, repo_root=repo_root), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return binding


def catalog_module_ids_from_allowed_modules(allowed_modules: list[str]) -> tuple[str, ...]:
    """Return only allowed module ids that currently exist in the product catalog."""
    seen: set[str] = set()
    module_ids: list[str] = []
    for module_id in allowed_modules:
        if module_id in seen or get_module_by_id(module_id) is None:
            continue
        seen.add(module_id)
        module_ids.append(module_id)
    return tuple(module_ids)


def collect_target_workspace_state(target: TargetRecord, repo_root: Path | None = None) -> TargetWorkspaceState:
    """Inspect a target workspace without creating or modifying files."""
    workspace = target_workspace_for_record(target, repo_root=repo_root)
    modules_root = workspace.root_path / "modules"
    bound_modules: list[str] = []
    if modules_root.is_dir():
        bound_modules = sorted(path.name for path in modules_root.iterdir() if path.is_dir())
    return TargetWorkspaceState(
        target_id=workspace.target_id,
        root_path=workspace.root_path,
        manifest_path=workspace.manifest_path,
        workspace_exists=workspace.root_path.is_dir(),
        manifest_exists=workspace.manifest_path.is_file(),
        bound_modules=tuple(bound_modules),
    )
