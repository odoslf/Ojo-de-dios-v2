"""Workspace primitives for module/tool execution areas.

The workspace layer creates concrete filesystem areas used by modules and future
approved tools. It only creates directories and structural manifests; it does not
execute tools, imply technique readiness, or mark reserved modules as functional.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.core.module_catalog import ModuleCatalogEntry, list_modules, require_module_by_id

WORKSPACE_SCHEMA_VERSION = 1
WORKSPACE_MANIFEST_FILENAME = "workspace_manifest.json"
TOOL_WORKSPACE_MANIFEST_FILENAME = "tool_workspace_manifest.json"
TOOL_RUN_MANIFEST_FILENAME = "tool_run_manifest.json"
STANDARD_WORKSPACE_DIRS = (
    "inputs",
    "outputs",
    "logs",
    "evidence",
    "reports",
    "tmp",
    "tool_runs",
    "tools",
)
TOOL_WORKSPACE_DIRS = (
    "inputs",
    "outputs",
    "logs",
    "evidence",
    "reports",
    "tmp",
    "tool_runs",
)
_TOOL_ID_PATTERN = re.compile(r"[^a-z0-9._-]+")



@dataclass(frozen=True, slots=True)
class ModuleWorkspace:
    """Concrete module workspace paths."""

    module_id: str
    root_path: Path
    manifest_path: Path
    standard_dirs: tuple[Path, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe workspace descriptor."""
        return {
            "module_id": self.module_id,
            "root_path": self.root_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "standard_dirs": [path.as_posix() for path in self.standard_dirs],
        }


@dataclass(frozen=True, slots=True)
class ToolWorkspace:
    """Concrete per-tool workspace paths inside a module workspace."""

    module_id: str
    tool_id: str
    root_path: Path
    manifest_path: Path
    standard_dirs: tuple[Path, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe per-tool workspace descriptor."""
        return {
            "module_id": self.module_id,
            "tool_id": self.tool_id,
            "root_path": self.root_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "standard_dirs": [path.as_posix() for path in self.standard_dirs],
        }


@dataclass(frozen=True, slots=True)
class ToolRunWorkspace:
    """Concrete per-run workspace for one tool invocation preparation."""

    module_id: str
    tool_id: str
    run_id: str
    root_path: Path
    manifest_path: Path
    input_path: Path
    output_path: Path
    log_path: Path
    evidence_path: Path
    tmp_path: Path

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe per-run workspace descriptor."""
        return {
            "module_id": self.module_id,
            "tool_id": self.tool_id,
            "run_id": self.run_id,
            "root_path": self.root_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "input_path": self.input_path.as_posix(),
            "output_path": self.output_path.as_posix(),
            "log_path": self.log_path.as_posix(),
            "evidence_path": self.evidence_path.as_posix(),
            "tmp_path": self.tmp_path.as_posix(),
        }


def _repo_path(repo_root: Path, relative_path: str) -> Path:
    """Resolve a catalog relative path and ensure it stays inside the repo root."""
    root = repo_root.resolve()
    resolved = (root / relative_path).resolve()
    if root != resolved and root not in resolved.parents:
        raise ValueError(f"Workspace path escapes repository root: {relative_path}.")
    return resolved


def workspace_for_module(module: ModuleCatalogEntry, repo_root: Path | None = None) -> ModuleWorkspace:
    """Return workspace paths for one module without creating directories."""
    root = Path.cwd() if repo_root is None else repo_root
    workspace_root = _repo_path(root, module.workspace_path)
    return ModuleWorkspace(
        module_id=module.module_id,
        root_path=workspace_root,
        manifest_path=workspace_root / WORKSPACE_MANIFEST_FILENAME,
        standard_dirs=tuple(workspace_root / dirname for dirname in STANDARD_WORKSPACE_DIRS),
    )


def build_workspace_manifest(module: ModuleCatalogEntry) -> dict[str, object]:
    """Build the structural workspace manifest for one module."""
    return {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "module_number": module.module_number,
        "module_id": module.module_id,
        "lifecycle": module.lifecycle,
        "readiness": module.readiness,
        "official": module.official,
        "reserved": module.reserved,
        "requires_user_definition": module.requires_user_definition,
        "workspace_path": module.workspace_path,
        "standard_dirs": list(STANDARD_WORKSPACE_DIRS),
        "execution_implied": False,
    }


def normalize_tool_id(tool_id: str) -> str:
    """Normalize a human/tool name into a safe workspace identifier."""
    raw = tool_id.strip().lower()
    if not raw:
        raise ValueError("Tool id cannot be empty.")
    if ".." in raw or "\\" in raw:
        raise ValueError("Tool id cannot contain path traversal characters.")
    if "/" in raw and " / " not in raw:
        raise ValueError("Tool id cannot contain path traversal characters.")
    raw = raw.replace(" / ", " ")
    normalized = _TOOL_ID_PATTERN.sub("-", raw).strip("-._")
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    if not normalized:
        raise ValueError("Tool id does not contain a usable identifier.")
    if len(normalized) > 80:
        raise ValueError("Tool id is too long for a workspace identifier.")
    return normalized


def _utc_now_iso() -> str:
    """Return a UTC timestamp suitable for workspace manifests."""
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def generate_tool_run_id() -> str:
    """Generate a collision-resistant, sortable tool run identifier."""
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"run-{timestamp}-{uuid4().hex[:12]}"


def normalize_run_id(run_id: str) -> str:
    """Normalize or validate a caller-provided run identifier."""
    return normalize_tool_id(run_id)


def tool_workspace_for_module(
    module_id: str,
    tool_id: str,
    repo_root: Path | None = None,
) -> ToolWorkspace:
    """Return per-tool workspace paths without creating directories."""
    module = require_module_by_id(module_id)
    normalized_tool_id = normalize_tool_id(tool_id)
    module_workspace = workspace_for_module(module, repo_root=repo_root)
    tool_root = module_workspace.root_path / "tools" / normalized_tool_id
    return ToolWorkspace(
        module_id=module.module_id,
        tool_id=normalized_tool_id,
        root_path=tool_root,
        manifest_path=tool_root / TOOL_WORKSPACE_MANIFEST_FILENAME,
        standard_dirs=tuple(tool_root / dirname for dirname in TOOL_WORKSPACE_DIRS),
    )


def build_tool_workspace_manifest(module_id: str, tool_id: str) -> dict[str, object]:
    """Build a structural manifest for one module-owned tool workspace."""
    module = require_module_by_id(module_id)
    normalized_tool_id = normalize_tool_id(tool_id)
    return {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "module_number": module.module_number,
        "module_id": module.module_id,
        "tool_id": normalized_tool_id,
        "workspace_path": f"{module.workspace_path}/tools/{normalized_tool_id}",
        "standard_dirs": list(TOOL_WORKSPACE_DIRS),
        "approval_required": True,
        "execution_implied": False,
        "tool_run_state": "not_executed",
        "user_data_boundary": "module_tool_workspace",
    }


def tool_run_workspace_for_module(
    module_id: str,
    tool_id: str,
    run_id: str,
    repo_root: Path | None = None,
) -> ToolRunWorkspace:
    """Return per-run workspace paths without creating directories."""
    tool_workspace = tool_workspace_for_module(module_id, tool_id, repo_root=repo_root)
    normalized_run_id = normalize_run_id(run_id)
    run_root = tool_workspace.root_path / "tool_runs" / normalized_run_id
    return ToolRunWorkspace(
        module_id=tool_workspace.module_id,
        tool_id=tool_workspace.tool_id,
        run_id=normalized_run_id,
        root_path=run_root,
        manifest_path=run_root / TOOL_RUN_MANIFEST_FILENAME,
        input_path=run_root / "inputs",
        output_path=run_root / "outputs",
        log_path=run_root / "logs",
        evidence_path=run_root / "evidence",
        tmp_path=run_root / "tmp",
    )


def build_tool_run_manifest(module_id: str, tool_id: str, run_id: str, created_at: str) -> dict[str, object]:
    """Build a structural manifest for a prepared tool run workspace."""
    module = require_module_by_id(module_id)
    normalized_tool_id = normalize_tool_id(tool_id)
    normalized_run_id = normalize_run_id(run_id)
    return {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "module_number": module.module_number,
        "module_id": module.module_id,
        "tool_id": normalized_tool_id,
        "run_id": normalized_run_id,
        "created_at": created_at,
        "workspace_path": f"{module.workspace_path}/tools/{normalized_tool_id}/tool_runs/{normalized_run_id}",
        "status": "prepared",
        "execution_requested": False,
        "execution_implied": False,
        "input_path": "inputs",
        "output_path": "outputs",
        "log_path": "logs",
        "evidence_path": "evidence",
        "tmp_path": "tmp",
    }


def ensure_module_workspace(module_id: str, repo_root: Path | None = None) -> ModuleWorkspace:
    """Create and validate the filesystem workspace for one catalog module."""
    module = require_module_by_id(module_id)
    workspace = workspace_for_module(module, repo_root=repo_root)
    workspace.root_path.mkdir(parents=True, exist_ok=True)
    for directory in workspace.standard_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    workspace.manifest_path.write_text(
        json.dumps(build_workspace_manifest(module), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return workspace


def ensure_all_module_workspaces(repo_root: Path | None = None) -> tuple[ModuleWorkspace, ...]:
    """Create workspaces for every catalog module slot in stable order."""
    return tuple(ensure_module_workspace(module.module_id, repo_root=repo_root) for module in list_modules())


def load_workspace_manifest(module_id: str, repo_root: Path | None = None) -> dict[str, object]:
    """Load a workspace manifest for an existing module workspace."""
    module = require_module_by_id(module_id)
    workspace = workspace_for_module(module, repo_root=repo_root)
    if not workspace.manifest_path.is_file():
        raise FileNotFoundError(f"Workspace manifest missing for module {module_id}.")
    loaded = json.loads(workspace.manifest_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Workspace manifest must be a JSON object for module {module_id}.")
    return loaded


def validate_workspace_manifest(module_id: str, repo_root: Path | None = None) -> None:
    """Validate that an existing workspace manifest matches the catalog contract."""
    module = require_module_by_id(module_id)
    manifest = load_workspace_manifest(module_id, repo_root=repo_root)
    expected = build_workspace_manifest(module)
    for key, expected_value in expected.items():
        if manifest.get(key) != expected_value:
            raise ValueError(
                f"Workspace manifest mismatch for {module_id}.{key}: "
                f"expected {expected_value!r}, got {manifest.get(key)!r}."
            )


def ensure_tool_workspace(
    module_id: str,
    tool_id: str,
    repo_root: Path | None = None,
) -> ToolWorkspace:
    """Create and validate a per-tool workspace inside a module workspace."""
    ensure_module_workspace(module_id, repo_root=repo_root)
    tool_workspace = tool_workspace_for_module(module_id, tool_id, repo_root=repo_root)
    tool_workspace.root_path.mkdir(parents=True, exist_ok=True)
    for directory in tool_workspace.standard_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    tool_workspace.manifest_path.write_text(
        json.dumps(build_tool_workspace_manifest(module_id, tool_workspace.tool_id), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return tool_workspace


def load_tool_workspace_manifest(
    module_id: str,
    tool_id: str,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Load a per-tool workspace manifest."""
    tool_workspace = tool_workspace_for_module(module_id, tool_id, repo_root=repo_root)
    if not tool_workspace.manifest_path.is_file():
        raise FileNotFoundError(f"Tool workspace manifest missing for {module_id}/{tool_workspace.tool_id}.")
    loaded = json.loads(tool_workspace.manifest_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Tool workspace manifest must be a JSON object for {module_id}/{tool_workspace.tool_id}.")
    return loaded


def validate_tool_workspace_manifest(
    module_id: str,
    tool_id: str,
    repo_root: Path | None = None,
) -> None:
    """Validate that a tool workspace manifest matches the structural contract."""
    normalized_tool_id = normalize_tool_id(tool_id)
    manifest = load_tool_workspace_manifest(module_id, normalized_tool_id, repo_root=repo_root)
    expected = build_tool_workspace_manifest(module_id, normalized_tool_id)
    for key, expected_value in expected.items():
        if manifest.get(key) != expected_value:
            raise ValueError(
                f"Tool workspace manifest mismatch for {module_id}/{normalized_tool_id}.{key}: "
                f"expected {expected_value!r}, got {manifest.get(key)!r}."
            )


def start_tool_run_workspace(
    module_id: str,
    tool_id: str,
    run_id: str | None = None,
    repo_root: Path | None = None,
) -> ToolRunWorkspace:
    """Create a prepared per-run workspace for a tool without executing it."""
    selected_run_id = generate_tool_run_id() if run_id is None else normalize_run_id(run_id)
    created_at = _utc_now_iso()
    ensure_tool_workspace(module_id, tool_id, repo_root=repo_root)
    run_workspace = tool_run_workspace_for_module(module_id, tool_id, selected_run_id, repo_root=repo_root)
    for directory in (
        run_workspace.root_path,
        run_workspace.input_path,
        run_workspace.output_path,
        run_workspace.log_path,
        run_workspace.evidence_path,
        run_workspace.tmp_path,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    run_workspace.manifest_path.write_text(
        json.dumps(
            build_tool_run_manifest(module_id, run_workspace.tool_id, run_workspace.run_id, created_at),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return run_workspace


def load_tool_run_manifest(
    module_id: str,
    tool_id: str,
    run_id: str,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Load a prepared tool-run workspace manifest."""
    run_workspace = tool_run_workspace_for_module(module_id, tool_id, run_id, repo_root=repo_root)
    if not run_workspace.manifest_path.is_file():
        raise FileNotFoundError(f"Tool run manifest missing for {module_id}/{run_workspace.tool_id}/{run_workspace.run_id}.")
    loaded = json.loads(run_workspace.manifest_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Tool run manifest must be a JSON object for {module_id}/{run_workspace.tool_id}.")
    return loaded


def validate_tool_run_manifest(
    module_id: str,
    tool_id: str,
    run_id: str,
    repo_root: Path | None = None,
) -> None:
    """Validate that a prepared tool-run manifest matches the structural contract."""
    manifest = load_tool_run_manifest(module_id, tool_id, run_id, repo_root=repo_root)
    expected = build_tool_run_manifest(
        module_id,
        normalize_tool_id(tool_id),
        normalize_run_id(run_id),
        str(manifest.get("created_at", "")),
    )
    for key, expected_value in expected.items():
        if manifest.get(key) != expected_value:
            raise ValueError(
                f"Tool run manifest mismatch for {module_id}/{tool_id}/{run_id}.{key}: "
                f"expected {expected_value!r}, got {manifest.get(key)!r}."
            )
