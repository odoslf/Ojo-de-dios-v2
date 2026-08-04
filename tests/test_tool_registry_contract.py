"""Tool registry contract tests."""

import pytest

from app.core.errors import ContractError
from app.core.tool_definition import ToolDefinition, list_tool_definitions_for_module
from app.core.tool_registry import create_empty_tool_registry, load_module_tool_registry, load_tool_registry_from_definitions


def test_empty_tool_registry_starts_empty() -> None:
    assert create_empty_tool_registry().count() == 0


def test_register_get_require_and_list_by_module() -> None:
    definition = next(definition for definition in list_tool_definitions_for_module("m01_osint") if definition.tool_id == "nmap")
    registry = create_empty_tool_registry()

    registry.register(definition)

    assert registry.count() == 1
    assert registry.get("m01_osint", "Nmap") == definition
    assert registry.require("m01_osint", "nmap") == definition
    assert registry.list_keys() == ["m01_osint/nmap"]
    assert registry.list_by_module("m01_osint") == [definition]
    assert registry.list_by_tool_id("nmap") == [definition]
    with pytest.raises(ContractError, match="not registered"):
        registry.require("m01_osint", "missing")


def test_duplicate_module_tool_pair_fails() -> None:
    definition = next(definition for definition in list_tool_definitions_for_module("m01_osint") if definition.tool_id == "nmap")
    registry = create_empty_tool_registry()
    registry.register(definition)

    with pytest.raises(ContractError, match="Duplicate tool definition"):
        registry.register(definition)


def test_registry_allows_same_tool_id_in_different_modules() -> None:
    definition = ToolDefinition(
        tool_id="shared-tool",
        display_name="Shared Tool",
        category="manual_process",
        module_ids=("m01_osint", "m02_vulnerabilities"),
        runtime="documented_only",
        workspace_path="storage/workspaces/shared/tools/shared-tool",
        approved_status="documented_planned",
        healthcheck_method="not_configured",
    )

    registry = load_tool_registry_from_definitions((definition,))

    assert registry.count() == 2
    assert registry.list_keys() == ["m01_osint/shared-tool", "m02_vulnerabilities/shared-tool"]
    assert registry.require("m01_osint", "shared-tool").module_ids == ("m01_osint",)
    assert registry.require("m02_vulnerabilities", "shared-tool").module_ids == ("m02_vulnerabilities",)


def test_load_module_tool_registry_from_real_definitions() -> None:
    registry = load_module_tool_registry("m01_osint")

    assert registry.count() >= 20
    assert "m01_osint/nmap" in registry.list_keys()
    assert registry.require("m01_osint", "have-i-been-pwned").display_name == "Have I Been Pwned"
    assert all(definition.execution_implied is False for definition in registry.list_all())
