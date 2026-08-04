"""Documentation-backed tool inventory helpers.

This layer reads the repository's documented module tool inventory and turns it
into JSON-safe metadata. It does not install, execute, approve, or version-lock
any tool; operational readiness remains the responsibility of ToolHealth,
VersionLock, policy checks, and explicit user approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.module_catalog import get_module_by_number, require_module_by_id
from app.core.workspace import ensure_tool_workspace, normalize_tool_id

TOOL_INVENTORY_SOURCE_PATH = Path("docs/MODULE_TOOL_INVENTORY.md")
DOCUMENTED_TOOL_APPROVED_STATUS = "documented_planned"
DOCUMENTED_TOOL_CATEGORY = "manual_process"
DOCUMENTED_TOOL_HEALTHCHECK_METHOD = "not_configured"


@dataclass(frozen=True, slots=True)
class DocumentedToolInventoryItem:
    """One tool/capability listed in docs/MODULE_TOOL_INVENTORY.md."""

    tool_id: str
    display_name: str
    category: str
    module_ids: tuple[str, ...]
    runtime: str
    source_url: str | None
    expected_version: str | None
    versionlock_id: str | None
    healthcheck_method: str
    approved_status: str
    source_path: str
    source_section: str
    workspace_path: str
    execution_implied: bool = False

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe documented inventory item."""
        return {
            "tool_id": self.tool_id,
            "display_name": self.display_name,
            "category": self.category,
            "module_ids": list(self.module_ids),
            "runtime": self.runtime,
            "source_url": self.source_url,
            "expected_version": self.expected_version,
            "versionlock_id": self.versionlock_id,
            "healthcheck_method": self.healthcheck_method,
            "approved_status": self.approved_status,
            "source_path": self.source_path,
            "source_section": self.source_section,
            "workspace_path": self.workspace_path,
            "execution_implied": self.execution_implied,
        }


def _clean_bullet_text(line: str) -> str:
    """Normalize a markdown bullet into a display name."""
    return line.strip()[2:].strip().rstrip(";.").strip()


def _module_id_from_section(section_title: str) -> str | None:
    """Map a Spanish module section title to a catalog module id."""
    marker = "## Módulo "
    if not section_title.startswith(marker):
        return None
    remainder = section_title[len(marker) :].strip()
    number_text = remainder.split(" ", 1)[0]
    if not number_text.isdigit():
        return None
    module = get_module_by_number(int(number_text))
    return None if module is None else module.module_id


def _iter_documented_tool_names(markdown_text: str) -> list[tuple[str, str, str]]:
    """Return (module_id, section_title, tool_name) entries from inventory markdown."""
    entries: list[tuple[str, str, str]] = []
    current_module_id: str | None = None
    current_section_title = ""
    collecting_tools = False
    saw_tool_bullet = False

    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current_section_title = line
            current_module_id = _module_id_from_section(line)
            collecting_tools = False
            saw_tool_bullet = False
            continue
        if current_module_id is None:
            continue
        if line.startswith("Herramientas/capacidades"):
            collecting_tools = True
            saw_tool_bullet = False
            continue
        if not collecting_tools:
            continue
        if line.startswith("- "):
            tool_name = _clean_bullet_text(line)
            if tool_name:
                entries.append((current_module_id, current_section_title, tool_name))
                saw_tool_bullet = True
            continue
        if saw_tool_bullet and line:
            collecting_tools = False
            saw_tool_bullet = False

    return entries


def documented_tool_item_from_name(
    module_id: str,
    section_title: str,
    display_name: str,
    source_path: Path = TOOL_INVENTORY_SOURCE_PATH,
) -> DocumentedToolInventoryItem:
    """Build one documented tool inventory item without inventing runtime metadata."""
    module = require_module_by_id(module_id)
    tool_id = normalize_tool_id(display_name.replace("/", " "))
    return DocumentedToolInventoryItem(
        tool_id=tool_id,
        display_name=display_name,
        category=DOCUMENTED_TOOL_CATEGORY,
        module_ids=(module.module_id,),
        runtime="documented_only",
        source_url=None,
        expected_version=None,
        versionlock_id=None,
        healthcheck_method=DOCUMENTED_TOOL_HEALTHCHECK_METHOD,
        approved_status=DOCUMENTED_TOOL_APPROVED_STATUS,
        source_path=source_path.as_posix(),
        source_section=section_title,
        workspace_path=f"{module.workspace_path}/tools/{tool_id}",
        execution_implied=False,
    )


def load_documented_tool_inventory(
    source_path: Path = TOOL_INVENTORY_SOURCE_PATH,
) -> tuple[DocumentedToolInventoryItem, ...]:
    """Load documented tool inventory from docs without installing or executing tools."""
    markdown_text = source_path.read_text(encoding="utf-8")
    return tuple(
        documented_tool_item_from_name(module_id, section_title, display_name, source_path=source_path)
        for module_id, section_title, display_name in _iter_documented_tool_names(markdown_text)
    )


def list_documented_tools_for_module(
    module_id: str,
    source_path: Path = TOOL_INVENTORY_SOURCE_PATH,
) -> tuple[DocumentedToolInventoryItem, ...]:
    """Return documented tools for one catalog module in documentation order."""
    module = require_module_by_id(module_id)
    return tuple(
        item for item in load_documented_tool_inventory(source_path=source_path) if module.module_id in item.module_ids
    )


def ensure_documented_tool_workspaces(
    module_id: str,
    repo_root: Path | None = None,
    source_path: Path = TOOL_INVENTORY_SOURCE_PATH,
) -> tuple[dict[str, object], ...]:
    """Create per-tool workspaces for the tools documented for one module."""
    workspaces: list[dict[str, object]] = []
    for item in list_documented_tools_for_module(module_id, source_path=source_path):
        workspaces.append(ensure_tool_workspace(module_id, item.tool_id, repo_root=repo_root).to_dict())
    return tuple(workspaces)
