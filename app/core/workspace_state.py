"""Filesystem state inspection for module/tool workspaces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.module_catalog import require_module_by_id
from app.core.tool_run_summary import summarize_tool_run_workspace
from app.core.workspace import TOOL_RUN_MANIFEST_FILENAME, TOOL_WORKSPACE_MANIFEST_FILENAME, workspace_for_module


@dataclass(frozen=True, slots=True)
class ToolRunWorkspaceState:
    """Current filesystem state for one prepared tool run."""

    run_id: str
    root_path: Path
    manifest_path: Path
    manifest_exists: bool
    status: str | None
    artifact_count: int
    total_artifact_bytes: int

    def to_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "root_path": self.root_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "manifest_exists": self.manifest_exists,
            "status": self.status,
            "artifact_count": self.artifact_count,
            "total_artifact_bytes": self.total_artifact_bytes,
        }


@dataclass(frozen=True, slots=True)
class ToolWorkspaceState:
    """Current filesystem state for one tool workspace."""

    tool_id: str
    root_path: Path
    manifest_path: Path
    manifest_exists: bool
    runs: tuple[ToolRunWorkspaceState, ...]

    @property
    def run_count(self) -> int:
        return len(self.runs)

    def to_dict(self) -> dict[str, object]:
        return {
            "tool_id": self.tool_id,
            "root_path": self.root_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "manifest_exists": self.manifest_exists,
            "run_count": self.run_count,
            "runs": [run.to_dict() for run in self.runs],
        }


@dataclass(frozen=True, slots=True)
class ModuleWorkspaceState:
    """Current filesystem state for one module workspace."""

    module_id: str
    root_path: Path
    manifest_path: Path
    workspace_exists: bool
    manifest_exists: bool
    tools: tuple[ToolWorkspaceState, ...]

    @property
    def tool_count(self) -> int:
        return len(self.tools)

    @property
    def run_count(self) -> int:
        return sum(tool.run_count for tool in self.tools)

    def to_dict(self) -> dict[str, object]:
        return {
            "module_id": self.module_id,
            "root_path": self.root_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "workspace_exists": self.workspace_exists,
            "manifest_exists": self.manifest_exists,
            "tool_count": self.tool_count,
            "run_count": self.run_count,
            "tools": [tool.to_dict() for tool in self.tools],
        }


def _collect_run_states(
    module_id: str,
    tool_id: str,
    tool_root: Path,
    repo_root: Path | None = None,
) -> tuple[ToolRunWorkspaceState, ...]:
    runs_root = tool_root / "tool_runs"
    if not runs_root.is_dir():
        return ()
    runs: list[ToolRunWorkspaceState] = []
    for run_root in sorted(path for path in runs_root.iterdir() if path.is_dir()):
        manifest_path = run_root / TOOL_RUN_MANIFEST_FILENAME
        manifest_exists = manifest_path.is_file()
        status = None
        artifact_count = 0
        total_artifact_bytes = 0
        if manifest_exists:
            summary = summarize_tool_run_workspace(module_id, tool_id, run_root.name, repo_root=repo_root)
            status = str(summary.status) if summary.status is not None else None
            artifact_count = summary.artifact_count
            total_artifact_bytes = summary.total_artifact_bytes
        runs.append(
            ToolRunWorkspaceState(
                run_id=run_root.name,
                root_path=run_root,
                manifest_path=manifest_path,
                manifest_exists=manifest_exists,
                status=status,
                artifact_count=artifact_count,
                total_artifact_bytes=total_artifact_bytes,
            )
        )
    return tuple(runs)


def _collect_tool_states(
    module_id: str,
    module_root: Path,
    repo_root: Path | None = None,
) -> tuple[ToolWorkspaceState, ...]:
    tools_root = module_root / "tools"
    if not tools_root.is_dir():
        return ()
    tools: list[ToolWorkspaceState] = []
    for tool_root in sorted(path for path in tools_root.iterdir() if path.is_dir()):
        manifest_path = tool_root / TOOL_WORKSPACE_MANIFEST_FILENAME
        tools.append(
            ToolWorkspaceState(
                tool_id=tool_root.name,
                root_path=tool_root,
                manifest_path=manifest_path,
                manifest_exists=manifest_path.is_file(),
                runs=_collect_run_states(module_id, tool_root.name, tool_root, repo_root=repo_root),
            )
        )
    return tuple(tools)


def collect_module_workspace_state(module_id: str, repo_root: Path | None = None) -> ModuleWorkspaceState:
    """Inspect one module workspace on disk without creating or modifying files."""
    module = require_module_by_id(module_id)
    workspace = workspace_for_module(module, repo_root=repo_root)
    return ModuleWorkspaceState(
        module_id=module.module_id,
        root_path=workspace.root_path,
        manifest_path=workspace.manifest_path,
        workspace_exists=workspace.root_path.is_dir(),
        manifest_exists=workspace.manifest_path.is_file(),
        tools=_collect_tool_states(module.module_id, workspace.root_path, repo_root=repo_root),
    )
