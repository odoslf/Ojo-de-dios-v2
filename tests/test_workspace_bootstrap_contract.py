"""Workspace bootstrap behavior tests."""

from pathlib import Path

from app.core.workspace import load_tool_workspace_manifest, load_workspace_manifest
from app.core.workspace_bootstrap import bootstrap_all_module_workspaces, bootstrap_module_workspace


def test_bootstrap_module_workspace_creates_module_and_documented_tool_workspaces(tmp_path: Path) -> None:
    result = bootstrap_module_workspace("m01_osint", repo_root=tmp_path)
    payload = result.to_dict()
    tool_ids = {workspace.tool_id for workspace in result.tool_workspaces}

    assert result.module_id == "m01_osint"
    assert result.documented_tool_count >= 20
    assert result.created_tool_workspace_count == result.documented_tool_count
    assert "nmap" in tool_ids
    assert "subfinder" in tool_ids
    assert payload["execution_implied"] is False

    module_manifest = load_workspace_manifest("m01_osint", repo_root=tmp_path)
    nmap_manifest = load_tool_workspace_manifest("m01_osint", "nmap", repo_root=tmp_path)
    assert module_manifest["module_id"] == "m01_osint"
    assert nmap_manifest["tool_id"] == "nmap"
    assert nmap_manifest["tool_run_state"] == "not_executed"


def test_bootstrap_module_workspace_can_create_only_module_structure(tmp_path: Path) -> None:
    result = bootstrap_module_workspace("m02_vulnerabilities", include_documented_tools=False, repo_root=tmp_path)

    assert result.module_workspace.manifest_path.is_file()
    assert result.documented_tool_count == 0
    assert result.created_tool_workspace_count == 0
    assert result.tool_workspaces == ()


def test_bootstrap_all_module_workspaces_preserves_catalog_order_and_reserved_choice(tmp_path: Path) -> None:
    summary = bootstrap_all_module_workspaces(include_documented_tools=False, include_reserved=False, repo_root=tmp_path)
    payload = summary.to_dict()

    assert summary.module_count == 16
    assert summary.tool_workspace_count == 0
    assert summary.results[0].module_id == "m01_osint"
    assert summary.results[-1].module_id == "m16_ops_quality"
    assert payload["execution_implied"] is False
