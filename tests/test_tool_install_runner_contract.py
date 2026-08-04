"""Tool install runner contract tests."""

import sys

from app.core.tool_install_plan import INSTALL_MANAGER_PIP, INSTALL_STATUS_NEEDS_METADATA, INSTALL_STATUS_READY, ToolInstallStep
from app.core.tool_install_runner import (
    INSTALL_EXECUTION_APPROVAL,
    INSTALL_EXECUTION_BLOCKED,
    INSTALL_EXECUTION_COMPLETED,
    INSTALL_EXECUTION_FAILED,
    INSTALL_EXECUTION_SKIPPED,
    execute_tool_install_step,
)


def _ready_step(*command_argv: str) -> ToolInstallStep:
    return ToolInstallStep(
        module_id="m16_ops_quality",
        tool_id="python-runtime-check",
        display_name="Python Runtime Check",
        status=INSTALL_STATUS_READY,
        manager=INSTALL_MANAGER_PIP,
        command_argv=tuple(command_argv),
        package_name="python-runtime-check",
        execution_performed=False,
    )


def test_runner_skips_ready_step_without_explicit_approval() -> None:
    receipt = execute_tool_install_step(_ready_step(sys.executable, "--version"))

    assert receipt.status == INSTALL_EXECUTION_SKIPPED
    assert receipt.execution_performed is False
    assert receipt.return_code is None


def test_runner_blocks_non_ready_step() -> None:
    step = ToolInstallStep(
        module_id="m01_osint",
        tool_id="nmap",
        display_name="Nmap",
        status=INSTALL_STATUS_NEEDS_METADATA,
        manager="apt",
        command_argv=("sudo", "apt-get", "install", "-y", "nmap"),
    )

    receipt = execute_tool_install_step(step, approval=INSTALL_EXECUTION_APPROVAL)

    assert receipt.status == INSTALL_EXECUTION_BLOCKED
    assert receipt.execution_performed is False


def test_runner_executes_argv_command_after_approval() -> None:
    receipt = execute_tool_install_step(
        _ready_step(sys.executable, "-c", "print('install-runner-ok')"),
        approval=INSTALL_EXECUTION_APPROVAL,
        timeout_seconds=10,
    )

    assert receipt.status == INSTALL_EXECUTION_COMPLETED
    assert receipt.execution_performed is True
    assert receipt.return_code == 0
    assert "install-runner-ok" in receipt.stdout


def test_runner_reports_non_zero_exit_and_redacts_secret_output() -> None:
    receipt = execute_tool_install_step(
        _ready_step(sys.executable, "-c", "import sys; print('token=abc123'); sys.exit(7)"),
        approval=INSTALL_EXECUTION_APPROVAL,
        timeout_seconds=10,
    )

    assert receipt.status == INSTALL_EXECUTION_FAILED
    assert receipt.execution_performed is True
    assert receipt.return_code == 7
    assert "abc123" not in receipt.stdout
    assert "token=<redacted>" in receipt.stdout
