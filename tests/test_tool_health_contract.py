"""ToolHealth contract tests."""

import sys

from app.core.tool_health import (
    TOOL_HEALTH_APPROVAL_REQUIRED,
    TOOL_HEALTH_MISSING_TOOL,
    TOOL_HEALTH_READY_CONTROLLED,
    TOOL_HEALTH_VERSION_LOCKED,
    TOOL_HEALTH_VERSION_UNKNOWN,
    ToolHealthSpec,
    check_tool_health,
)
from app.core.version_lock import (
    RUNTIME_PYTHON,
    create_locked_entry,
    create_missing_lock,
    create_needs_review_entry,
)


def _python_lock(resolved_version: str):
    return create_locked_entry(
        tool_id="python.runtime",
        tool_name="Python runtime",
        module_id="m16_ops_quality",
        recommended_version=resolved_version,
        resolved_version=resolved_version,
        runtime=RUNTIME_PYTHON,
    )


def test_tool_health_reports_missing_tool_without_fake_success() -> None:
    spec = ToolHealthSpec(tool_id="missing.tool", executable="ojo-de-dios-tool-that-does-not-exist")
    lock = create_missing_lock("missing.tool", "Missing Tool", "m16_ops_quality", "1.0.0", runtime=RUNTIME_PYTHON)

    result = check_tool_health(spec, lock)

    assert result.status == TOOL_HEALTH_MISSING_TOOL
    assert result.executable_path == ""


def test_tool_health_reports_ready_when_version_matches_lock() -> None:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    spec = ToolHealthSpec(tool_id="python.runtime", executable=sys.executable, version_args=("--version",))

    result = check_tool_health(spec, _python_lock(version))

    assert result.status == TOOL_HEALTH_READY_CONTROLLED
    assert result.executable_path
    assert version in result.version_output


def test_tool_health_reports_version_unknown_when_version_does_not_match() -> None:
    spec = ToolHealthSpec(tool_id="python.runtime", executable=sys.executable, version_args=("--version",))

    result = check_tool_health(spec, _python_lock("0.0.0-not-installed"))

    assert result.status == TOOL_HEALTH_VERSION_UNKNOWN
    assert "Python" in result.version_output


def test_tool_health_reports_version_locked_when_no_version_command_is_configured() -> None:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    spec = ToolHealthSpec(tool_id="python.runtime", executable=sys.executable)

    result = check_tool_health(spec, _python_lock(version))

    assert result.status == TOOL_HEALTH_VERSION_LOCKED
    assert result.version_output == ""


def test_tool_health_reports_approval_required_for_needs_review_lock() -> None:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    spec = ToolHealthSpec(tool_id="python.runtime", executable=sys.executable, version_args=("--version",))
    lock = create_needs_review_entry(
        "python.runtime",
        "Python runtime",
        "m16_ops_quality",
        recommended_version=version,
        resolved_version=version,
        runtime=RUNTIME_PYTHON,
    )

    result = check_tool_health(spec, lock)

    assert result.status == TOOL_HEALTH_APPROVAL_REQUIRED


def test_tool_health_result_is_json_safe_and_contains_versionlock_status() -> None:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    spec = ToolHealthSpec(tool_id="python.runtime", executable=sys.executable)

    payload = check_tool_health(spec, _python_lock(version)).to_dict()

    assert payload["tool_id"] == "python.runtime"
    assert payload["module_id"] == "m16_ops_quality"
    assert payload["version_lock_status"] == "LOCKED"
