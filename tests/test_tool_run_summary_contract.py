"""Tool-run summary behavior tests."""

from pathlib import Path

from app.core.tool_run_summary import summarize_tool_run_workspace
from app.core.workspace import start_tool_run_workspace
from app.core.workspace_artifacts import write_tool_run_input_artifact, write_tool_run_output_artifact


def test_tool_run_summary_counts_artifacts_by_type(tmp_path: Path) -> None:
    start_tool_run_workspace("m01_osint", "Nmap", run_id="summary-run", repo_root=tmp_path)
    write_tool_run_input_artifact(
        "m01_osint",
        "nmap",
        "summary-run",
        "target",
        {"host": "192.0.2.10"},
        repo_root=tmp_path,
    )
    write_tool_run_output_artifact(
        "m01_osint",
        "nmap",
        "summary-run",
        "scan-result",
        {"open_ports": [443]},
        repo_root=tmp_path,
    )

    summary = summarize_tool_run_workspace("m01_osint", "Nmap", "summary-run", repo_root=tmp_path)

    assert summary.module_id == "m01_osint"
    assert summary.tool_id == "nmap"
    assert summary.run_id == "summary-run"
    assert summary.manifest["status"] == "prepared"
    assert summary.artifact_count == 2
    assert summary.artifact_counts_by_type["input"] == 1
    assert summary.artifact_counts_by_type["output"] == 1
    assert summary.total_artifact_bytes > 0
    assert {artifact.artifact_name for artifact in summary.artifacts} == {"target", "scan-result"}
