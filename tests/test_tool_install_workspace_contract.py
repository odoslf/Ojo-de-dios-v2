"""Tool install workspace persistence contract tests."""

from pathlib import Path

from app.core.tool_install_workspace import (
    INSTALL_PLAN_FILENAME,
    prepare_module_tool_install_plan,
    read_prepared_module_tool_install_plan,
)


def test_prepare_module_tool_install_plan_persists_reviewable_plan(tmp_path: Path) -> None:
    persisted = prepare_module_tool_install_plan("m01_osint", repo_root=tmp_path)

    assert persisted.module_id == "m01_osint"
    assert persisted.path.name == INSTALL_PLAN_FILENAME
    assert persisted.path.is_file()
    assert len(persisted.sha256) == 64
    assert persisted.byte_count > 0
    assert persisted.plan.execution_performed is False
    assert persisted.plan.count >= 20


def test_read_prepared_module_tool_install_plan_returns_payload_and_metadata(tmp_path: Path) -> None:
    prepared = prepare_module_tool_install_plan("m01_osint", repo_root=tmp_path)

    recovered, payload = read_prepared_module_tool_install_plan("m01_osint", repo_root=tmp_path)

    assert recovered.sha256 == prepared.sha256
    assert recovered.byte_count == prepared.byte_count
    assert payload["module_id"] == "m01_osint"
    assert payload["execution_performed"] is False
    assert payload["approval_required_before_execution"] is True
    assert payload["install_plan"]["execution_performed"] is False
