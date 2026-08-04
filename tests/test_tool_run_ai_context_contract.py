"""Tool-run AI context behavior tests."""

from pathlib import Path

from app.ai.tool_run_context import build_tool_run_context_pack
from app.core.workspace import start_tool_run_workspace
from app.core.workspace_artifacts import write_tool_run_input_artifact, write_tool_run_output_artifact


def test_tool_run_context_pack_includes_redacted_artifact_payloads(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    start_tool_run_workspace("m01_osint", "Nmap", run_id="ai-context-run")
    write_tool_run_input_artifact(
        "m01_osint",
        "nmap",
        "ai-context-run",
        "target",
        {"host": "example.test", "api_key": "secret-value"},
    )
    write_tool_run_output_artifact(
        "m01_osint",
        "nmap",
        "ai-context-run",
        "scan-result",
        {"ports": [443], "nested": {"token": "hidden"}},
    )

    context_pack = build_tool_run_context_pack("m01_osint", "Nmap", "ai-context-run")
    payload = context_pack.to_dict()

    assert payload["pack_type"] == "tool_run_context_pack"
    assert payload["external_ai_call_performed"] is False
    assert payload["summary"]["artifact_count"] == 2
    assert payload["artifact_payload_count"] == 2
    encoded = str(payload)
    assert "secret-value" not in encoded
    assert "hidden" not in encoded
    assert "***REDACTED***" in encoded
    assert len(payload["checksum"]) == 64
