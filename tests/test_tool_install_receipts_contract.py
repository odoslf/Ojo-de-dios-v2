"""Tool install receipt persistence contract tests."""

import sys
from pathlib import Path

from app.core.tool_install_plan import INSTALL_MANAGER_PIP, INSTALL_STATUS_READY, ToolInstallStep
from app.core.tool_install_receipts import list_tool_install_receipts, read_tool_install_receipt, write_tool_install_receipt
from app.core.tool_install_runner import INSTALL_EXECUTION_APPROVAL, INSTALL_EXECUTION_COMPLETED, execute_tool_install_step


def _receipt():
    step = ToolInstallStep(
        module_id="m16_ops_quality",
        tool_id="python-runtime-check",
        display_name="Python Runtime Check",
        status=INSTALL_STATUS_READY,
        manager=INSTALL_MANAGER_PIP,
        command_argv=(sys.executable, "-c", "print('receipt-ok')"),
        package_name="python-runtime-check",
    )
    return execute_tool_install_step(step, approval=INSTALL_EXECUTION_APPROVAL, timeout_seconds=10)


def test_write_and_read_tool_install_receipt_roundtrips_metadata(tmp_path: Path) -> None:
    receipt = _receipt()

    persisted = write_tool_install_receipt(receipt, receipt_id="receipt-ok", repo_root=tmp_path)
    recovered = read_tool_install_receipt("m16_ops_quality", "receipt-ok", repo_root=tmp_path)

    assert receipt.status == INSTALL_EXECUTION_COMPLETED
    assert persisted.path.is_file()
    assert persisted.sha256 == recovered.sha256
    assert persisted.byte_count == recovered.byte_count
    assert recovered.receipt.stdout == receipt.stdout
    assert recovered.receipt.execution_performed is True


def test_list_tool_install_receipts_returns_sorted_receipts(tmp_path: Path) -> None:
    receipt = _receipt()
    write_tool_install_receipt(receipt, receipt_id="receipt-b", repo_root=tmp_path)
    write_tool_install_receipt(receipt, receipt_id="receipt-a", repo_root=tmp_path)

    receipts = list_tool_install_receipts("m16_ops_quality", repo_root=tmp_path)

    assert [item.receipt_id for item in receipts] == ["receipt-a", "receipt-b"]
    assert all(item.receipt.execution_performed for item in receipts)
