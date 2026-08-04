"""Documentation-backed tool inventory contract tests."""

from pathlib import Path

from app.core.tool_inventory import (
    DOCUMENTED_TOOL_APPROVED_STATUS,
    ensure_documented_tool_workspaces,
    list_documented_tools_for_module,
    load_documented_tool_inventory,
)
from app.core.workspace import load_tool_workspace_manifest


def test_documented_tool_inventory_loads_real_module_tool_names() -> None:
    inventory = load_documented_tool_inventory()
    tool_ids = {item.tool_id for item in inventory}

    assert "nmap" in tool_ids
    assert "subfinder" in tool_ids
    assert "nuclei" in tool_ids
    assert "hydra" in tool_ids
    assert all(item.execution_implied is False for item in inventory)
    assert all(item.approved_status == DOCUMENTED_TOOL_APPROVED_STATUS for item in inventory)


def test_documented_tools_for_module_include_workspace_paths_without_versions() -> None:
    osint_tools = list_documented_tools_for_module("m01_osint")
    nmap = next(item for item in osint_tools if item.tool_id == "nmap")

    assert len(osint_tools) >= 20
    assert nmap.display_name == "Nmap"
    assert nmap.module_ids == ("m01_osint",)
    assert nmap.workspace_path == "storage/workspaces/m01_osint/tools/nmap"
    assert nmap.expected_version is None
    assert nmap.versionlock_id is None
    assert nmap.healthcheck_method == "not_configured"


def test_documented_tool_inventory_does_not_include_capability_bullets_as_tools() -> None:
    osint_tool_ids = {item.tool_id for item in list_documented_tools_for_module("m01_osint")}

    assert "resoluci-n-de-dominio" not in osint_tool_ids
    assert "fingerprint-web" not in osint_tool_ids


def test_ensure_documented_tool_workspaces_creates_workspaces_from_docs(tmp_path: Path) -> None:
    workspaces = ensure_documented_tool_workspaces("m01_osint", repo_root=tmp_path)
    workspace_ids = {workspace["tool_id"] for workspace in workspaces}

    assert "nmap" in workspace_ids
    assert "have-i-been-pwned" in workspace_ids

    nmap_manifest = load_tool_workspace_manifest("m01_osint", "nmap", repo_root=tmp_path)
    assert nmap_manifest["workspace_path"] == "storage/workspaces/m01_osint/tools/nmap"
    assert nmap_manifest["execution_implied"] is False
