"""Tool-run lifecycle behavior tests."""

from pathlib import Path

from app.core.tool_run_lifecycle import update_tool_run_status
from app.core.workspace import load_tool_run_manifest, start_tool_run_workspace


def test_update_tool_run_status_persists_lifecycle_fields(tmp_path: Path) -> None:
    start_tool_run_workspace("m01_osint", "Nmap", run_id="lifecycle-run", repo_root=tmp_path)

    running = update_tool_run_status(
        "m01_osint",
        "Nmap",
        "lifecycle-run",
        "running",
        note="operator started local lab run",
        repo_root=tmp_path,
    )
    completed = update_tool_run_status("m01_osint", "nmap", "lifecycle-run", "completed", repo_root=tmp_path)
    manifest = load_tool_run_manifest("m01_osint", "nmap", "lifecycle-run", repo_root=tmp_path)

    assert running.previous_status == "prepared"
    assert running.status == "running"
    assert completed.previous_status == "running"
    assert completed.status == "completed"
    assert manifest["status"] == "completed"
    assert manifest["started_at"]
    assert manifest["finished_at"]
    assert manifest["status_note"] == "operator started local lab run"
