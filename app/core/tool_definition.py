"""Validated tool definition contracts built from the documented inventory."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

from app.core.errors import ContractError
from app.core.module_catalog import require_module_by_id
from app.core.tool_inventory import DocumentedToolInventoryItem, list_documented_tools_for_module, load_documented_tool_inventory
from app.core.workspace import normalize_tool_id

TOOL_CATEGORIES = {
    "binary_tool",
    "python_package",
    "node_package",
    "docker_image",
    "cloud_api",
    "local_ai",
    "external_ai",
    "hardware",
    "model",
    "manual_process",
}
TOOL_DEFINITION_SCHEMA_VERSION = 1
TOOL_APPROVAL_REQUIRED = "approval_required"


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """Validated metadata for one tool or capability before runtime registration."""

    tool_id: str
    display_name: str
    category: str
    module_ids: tuple[str, ...]
    runtime: str
    workspace_path: str
    approved_status: str
    healthcheck_method: str
    source_url: str | None = None
    expected_version: str | None = None
    versionlock_id: str | None = None
    approval_policy: str = TOOL_APPROVAL_REQUIRED
    execution_implied: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: int = TOOL_DEFINITION_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tool_id": self.tool_id,
            "display_name": self.display_name,
            "category": self.category,
            "module_ids": list(self.module_ids),
            "runtime": self.runtime,
            "workspace_path": self.workspace_path,
            "approved_status": self.approved_status,
            "healthcheck_method": self.healthcheck_method,
            "source_url": self.source_url,
            "expected_version": self.expected_version,
            "versionlock_id": self.versionlock_id,
            "approval_policy": self.approval_policy,
            "execution_implied": self.execution_implied,
            "metadata": self.metadata,
        }


def _validate_optional_url(source_url: str | None) -> None:
    if source_url is None:
        return
    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ContractError("Tool source_url must be an absolute http(s) URL.")


def validate_tool_definition(definition: ToolDefinition) -> None:
    """Validate a tool definition without installing or executing anything."""
    if definition.schema_version != TOOL_DEFINITION_SCHEMA_VERSION:
        raise ContractError("Unsupported tool definition schema version.")
    if normalize_tool_id(definition.tool_id) != definition.tool_id:
        raise ContractError("Tool id must already be normalized.")
    if not definition.display_name.strip():
        raise ContractError("Tool display_name cannot be empty.")
    if definition.category not in TOOL_CATEGORIES:
        raise ContractError(f"Unsupported tool category: {definition.category}.")
    if not definition.module_ids:
        raise ContractError("Tool definition must reference at least one module.")
    for module_id in definition.module_ids:
        require_module_by_id(module_id)
    if not definition.runtime.strip():
        raise ContractError("Tool runtime cannot be empty.")
    if not definition.workspace_path.strip():
        raise ContractError("Tool workspace_path cannot be empty.")
    if definition.execution_implied:
        raise ContractError("Tool definitions cannot imply execution readiness.")
    _validate_optional_url(definition.source_url)


def tool_definition_from_inventory_item(item: DocumentedToolInventoryItem) -> ToolDefinition:
    """Convert a documentation-backed inventory item into a validated tool definition."""
    definition = ToolDefinition(
        tool_id=item.tool_id,
        display_name=item.display_name,
        category=item.category,
        module_ids=item.module_ids,
        runtime=item.runtime,
        workspace_path=item.workspace_path,
        approved_status=item.approved_status,
        healthcheck_method=item.healthcheck_method,
        source_url=item.source_url,
        expected_version=item.expected_version,
        versionlock_id=item.versionlock_id,
        execution_implied=item.execution_implied,
        metadata={
            "source_path": item.source_path,
            "source_section": item.source_section,
        },
    )
    validate_tool_definition(definition)
    return definition


def load_tool_definitions() -> tuple[ToolDefinition, ...]:
    """Load validated tool definitions for all documented inventory items."""
    return tuple(tool_definition_from_inventory_item(item) for item in load_documented_tool_inventory())


def list_tool_definitions_for_module(module_id: str) -> tuple[ToolDefinition, ...]:
    """Load validated tool definitions for one catalog module."""
    require_module_by_id(module_id)
    return tuple(tool_definition_from_inventory_item(item) for item in list_documented_tools_for_module(module_id))
