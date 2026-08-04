"""Workspace bootstrap operations for modules and documented tools.

Bootstrap creates the concrete filesystem structure used by the application. It
is intentionally limited to directories and structural manifests; it never
installs tools, runs tools, marks success, or changes approval/version state.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.module_catalog import list_modules, require_module_by_id
from app.core.tool_inventory import list_documented_tools_for_module
from app.core.workspace import ModuleWorkspace, ToolWorkspace, ensure_module_workspace, ensure_tool_workspace


@dataclass(frozen=True, slots=True)
class ModuleWorkspaceBootstrapResult:
    """Result of bootstrapping one module workspace and its documented tools."""

    module_id: str
    module_workspace: ModuleWorkspace
    tool_workspaces: tuple[ToolWorkspace, ...]
    documented_tool_count: int
    created_tool_workspace_count: int
    execution_implied: bool = False

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe bootstrap result."""
        return {
            "module_id": self.module_id,
            "module_workspace": self.module_workspace.to_dict(),
            "tool_workspaces": [workspace.to_dict() for workspace in self.tool_workspaces],
            "documented_tool_count": self.documented_tool_count,
            "created_tool_workspace_count": self.created_tool_workspace_count,
            "execution_implied": self.execution_implied,
        }


@dataclass(frozen=True, slots=True)
class WorkspaceBootstrapSummary:
    """Summary for a multi-module workspace bootstrap run."""

    results: tuple[ModuleWorkspaceBootstrapResult, ...]
    execution_implied: bool = False

    @property
    def module_count(self) -> int:
        """Return number of bootstrapped module workspaces."""
        return len(self.results)

    @property
    def tool_workspace_count(self) -> int:
        """Return total created documented-tool workspaces."""
        return sum(result.created_tool_workspace_count for result in self.results)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe bootstrap summary."""
        return {
            "module_count": self.module_count,
            "tool_workspace_count": self.tool_workspace_count,
            "execution_implied": self.execution_implied,
            "results": [result.to_dict() for result in self.results],
        }


def bootstrap_module_workspace(
    module_id: str,
    include_documented_tools: bool = True,
    repo_root: Path | None = None,
) -> ModuleWorkspaceBootstrapResult:
    """Create one module workspace plus workspaces for documented tools."""
    module = require_module_by_id(module_id)
    module_workspace = ensure_module_workspace(module.module_id, repo_root=repo_root)
    documented_tools = list_documented_tools_for_module(module.module_id) if include_documented_tools else ()
    tool_workspaces = tuple(
        ensure_tool_workspace(module.module_id, item.tool_id, repo_root=repo_root)
        for item in documented_tools
    )
    return ModuleWorkspaceBootstrapResult(
        module_id=module.module_id,
        module_workspace=module_workspace,
        tool_workspaces=tool_workspaces,
        documented_tool_count=len(documented_tools),
        created_tool_workspace_count=len(tool_workspaces),
        execution_implied=False,
    )


def bootstrap_all_module_workspaces(
    include_documented_tools: bool = True,
    include_reserved: bool = True,
    repo_root: Path | None = None,
) -> WorkspaceBootstrapSummary:
    """Create workspaces for all selected catalog modules in stable order."""
    results = tuple(
        bootstrap_module_workspace(
            module.module_id,
            include_documented_tools=include_documented_tools,
            repo_root=repo_root,
        )
        for module in list_modules(include_reserved=include_reserved)
    )
    return WorkspaceBootstrapSummary(results=results, execution_implied=False)
