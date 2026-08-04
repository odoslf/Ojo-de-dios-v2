"""Workspace filesystem state inspection tests."""

from pathlib import Path

from app.core.tool_run_lifecycle import update_tool_run_status
from app.core.workspace import start_tool_run_workspace
from app.core.workspace_artifacts import write_tool_run_input_artifact
from app.core.workspace_bootstrap import bootstrap_module_workspace
from app.core.workspace_state import collect_module_workspace_state


def test_collect_module_workspace_state_reports_missing_workspace_without_creating(tmp_path: Path) -> None:
    state = collect_module_workspace_state("m01_osint", repo_root=tmp_path)

    assert state.module_id == "m01_osint"
    assert state.workspace_exists is False
    assert state.manifest_exists is False
    assert state.tool_count == 0
    assert state.run_count == 0
    assert not state.root_path.exists()


def test_collect_module_workspace_state_reports_tools_and_runs(tmp_path: Path) -> None:
    bootstrap_module_workspace("m01_osint", repo_root=tmp_path)
    start_tool_run_workspace("m01_osint", "Nmap", run_id="first-pass", repo_root=tmp_path)
    write_tool_run_input_artifact(
        "m01_osint",
        "nmap",
        "first-pass",
        "target",
        {"host": "example.test"},
        repo_root=tmp_path,
    )
    update_tool_run_status("m01_osint", "nmap", "first-pass", "completed", repo_root=tmp_path)
    start_tool_run_workspace("m01_osint", "Subfinder", run_id="subdomains", repo_root=tmp_path)

    state = collect_module_workspace_state("m01_osint", repo_root=tmp_path)
    payload = state.to_dict()
    tools = {tool.tool_id: tool for tool in state.tools}

    assert state.workspace_exists is True
    assert state.manifest_exists is True
    assert state.tool_count >= 20
    assert state.run_count == 2
    assert tools["nmap"].run_count == 1
    assert tools["nmap"].runs[0].run_id == "first-pass"
    assert tools["nmap"].runs[0].status == "completed"
    assert tools["nmap"].runs[0].artifact_count == 1
    assert tools["nmap"].runs[0].total_artifact_bytes > 0
    assert tools["subfinder"].run_count == 1
    assert payload["tools"]
