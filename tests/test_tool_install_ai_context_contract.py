"""Tool install AI context pack contract tests."""

import sys
from pathlib import Path

from app.ai.tool_install_context import build_tool_install_context_pack
from app.core.tool_install_plan import INSTALL_MANAGER_PIP, INSTALL_STATUS_READY, ToolInstallStep
from app.core.tool_install_receipts import write_tool_install_receipt
from app.core.tool_install_runner import INSTALL_EXECUTION_APPROVAL, execute_tool_install_step
from app.core.tool_install_workspace import prepare_module_tool_install_plan


def test_install_context_pack_uses_generated_plan_without_execution(tmp_path: Path) -> None:
    context = build_tool_install_context_pack("m01_osint", repo_root=tmp_path)

    assert context.module_id == "m01_osint"
    assert context.plan_prepared is False
    assert context.external_ai_call_performed is False
    assert context.plan["execution_performed"] is False
    assert context.plan["count"] >= 20
    assert len(context.checksum) == 64


def test_install_context_pack_includes_prepared_plan_and_bounded_receipts(tmp_path: Path) -> None:
    prepare_module_tool_install_plan("m16_ops_quality", repo_root=tmp_path)
    step = ToolInstallStep(
        module_id="m16_ops_quality",
        tool_id="python-runtime-check",
        display_name="Python Runtime Check",
        status=INSTALL_STATUS_READY,
        manager=INSTALL_MANAGER_PIP,
        command_argv=(sys.executable, "-c", "print('token=abc123')"),
        package_name="python-runtime-check",
    )
    receipt = execute_tool_install_step(step, approval=INSTALL_EXECUTION_APPROVAL, timeout_seconds=10)
    write_tool_install_receipt(receipt, receipt_id="receipt-ai", repo_root=tmp_path)

    context = build_tool_install_context_pack("m16_ops_quality", repo_root=tmp_path)
    payload = context.to_dict()

    assert payload["plan_prepared"] is True
    assert payload["external_ai_call_performed"] is False
    assert payload["receipts"][0]["receipt_id"] == "receipt-ai"
    assert "abc123" not in payload["receipts"][0]["stdout_excerpt"]
    assert payload["receipts"][0]["execution_performed"] is True
