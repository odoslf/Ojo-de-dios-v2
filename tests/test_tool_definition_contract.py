"""Tool definition contract tests."""

import pytest

from app.core.errors import ContractError
from app.core.tool_definition import (
    TOOL_APPROVAL_REQUIRED,
    ToolDefinition,
    list_tool_definitions_for_module,
    tool_definition_from_inventory_item,
    validate_tool_definition,
)
from app.core.tool_inventory import list_documented_tools_for_module


def test_tool_definitions_are_built_from_real_documented_inventory() -> None:
    definitions = list_tool_definitions_for_module("m01_osint")
    nmap = next(definition for definition in definitions if definition.tool_id == "nmap")

    assert len(definitions) >= 20
    assert nmap.display_name == "Nmap"
    assert nmap.module_ids == ("m01_osint",)
    assert nmap.workspace_path == "storage/workspaces/m01_osint/tools/nmap"
    assert nmap.approval_policy == TOOL_APPROVAL_REQUIRED
    assert nmap.execution_implied is False
    assert nmap.metadata["source_path"] == "docs/MODULE_TOOL_INVENTORY.md"


def test_inventory_item_to_tool_definition_preserves_contract_fields() -> None:
    item = next(item for item in list_documented_tools_for_module("m01_osint") if item.tool_id == "subfinder")
    definition = tool_definition_from_inventory_item(item)

    assert definition.tool_id == "subfinder"
    assert definition.category == item.category
    assert definition.healthcheck_method == item.healthcheck_method
    assert definition.to_dict()["schema_version"] == 1


def test_tool_definition_validation_rejects_execution_ready_claims() -> None:
    definition = ToolDefinition(
        tool_id="nmap",
        display_name="Nmap",
        category="manual_process",
        module_ids=("m01_osint",),
        runtime="documented_only",
        workspace_path="storage/workspaces/m01_osint/tools/nmap",
        approved_status="documented_planned",
        healthcheck_method="not_configured",
        execution_implied=True,
    )

    with pytest.raises(ContractError, match="cannot imply execution"):
        validate_tool_definition(definition)


def test_tool_definition_validation_rejects_unknown_category() -> None:
    definition = ToolDefinition(
        tool_id="nmap",
        display_name="Nmap",
        category="unknown",
        module_ids=("m01_osint",),
        runtime="documented_only",
        workspace_path="storage/workspaces/m01_osint/tools/nmap",
        approved_status="documented_planned",
        healthcheck_method="not_configured",
    )

    with pytest.raises(ContractError, match="Unsupported tool category"):
        validate_tool_definition(definition)
