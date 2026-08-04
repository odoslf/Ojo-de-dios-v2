"""Version lock contract tests."""

import pytest

from app.core.errors import ContractError
from app.core.tool_definition import ToolDefinition
from app.core.tool_inventory import DOCUMENTED_TOOL_CATEGORY
from app.core.version_lock import (
    RUNTIME_CUSTOM,
    RUNTIME_PYTHON,
    VERSION_LOCK_STATUS_LOCKED,
    VERSION_LOCK_STATUS_MISSING,
    VERSION_LOCK_STATUS_NEEDS_REVIEW,
    VERSION_LOCK_RECOMMENDED_UNRESOLVED,
    VersionLockEntry,
    create_locked_entry,
    create_missing_lock,
    create_needs_review_entry,
    create_needs_review_lock_from_tool_definition,
    is_latest_release_lock,
    runtime_for_tool_definition,
    validate_version_lock_entry,
    version_lock_id_for_tool,
)


def _locked_entry(**overrides) -> VersionLockEntry:
    data = {
        "tool_id": "tool-1",
        "tool_name": "Tool One",
        "module_id": "module-1",
        "recommended_version": "1.0.0",
        "resolved_version": "1.0.0",
        "source_url": "https://example.invalid/releases/tool-1",
        "runtime": RUNTIME_CUSTOM,
        "binary_hash": "0123456789abcdef",
        "locked_at": "2026-05-30T00:00:00+00:00",
        "status": VERSION_LOCK_STATUS_LOCKED,
    }
    data.update(overrides)
    return VersionLockEntry(**data)


def test_is_latest_release_lock_accepts_exact_value() -> None:
    assert is_latest_release_lock("latest-release-lock") is True


def test_is_latest_release_lock_accepts_trimmed_case_insensitive_value() -> None:
    assert is_latest_release_lock("  LATEST-RELEASE-LOCK  ") is True


def test_validate_version_lock_entry_accepts_valid_locked_entry() -> None:
    validate_version_lock_entry(_locked_entry())


def test_locked_without_resolved_version_raises_contract_error() -> None:
    with pytest.raises(ContractError):
        validate_version_lock_entry(_locked_entry(resolved_version=""))


def test_missing_with_resolved_version_raises_contract_error() -> None:
    with pytest.raises(ContractError):
        validate_version_lock_entry(
            _locked_entry(
                status=VERSION_LOCK_STATUS_MISSING,
                resolved_version="1.0.0",
                binary_hash="",
            )
        )


def test_invalid_runtime_raises_contract_error() -> None:
    with pytest.raises(ContractError):
        validate_version_lock_entry(_locked_entry(runtime="invalid"))


def test_invalid_status_raises_contract_error() -> None:
    with pytest.raises(ContractError):
        validate_version_lock_entry(_locked_entry(status="INVALID"))


def test_invalid_source_url_raises_contract_error() -> None:
    with pytest.raises(ContractError):
        validate_version_lock_entry(_locked_entry(source_url="file:///tmp/tool"))


def test_create_missing_lock_returns_missing_without_resolved_version() -> None:
    entry = create_missing_lock("tool-1", "Tool One", "module-1", "1.0.0")

    assert entry.status == VERSION_LOCK_STATUS_MISSING
    assert entry.resolved_version == ""
    assert entry.locked_at


def test_create_locked_entry_returns_locked_with_locked_at() -> None:
    entry = create_locked_entry("tool-1", "Tool One", "module-1", "1.0.0", "1.0.0", RUNTIME_CUSTOM)

    assert entry.status == VERSION_LOCK_STATUS_LOCKED
    assert entry.locked_at


def test_create_needs_review_entry_returns_needs_review() -> None:
    entry = create_needs_review_entry("tool-1", "Tool One", "module-1", "latest-release-lock")

    assert entry.status == VERSION_LOCK_STATUS_NEEDS_REVIEW
    assert entry.locked_at


def test_version_lock_id_for_tool_is_module_scoped_and_normalized() -> None:
    assert version_lock_id_for_tool("m01_osint", "Nmap Scanner") == "m01_osint/nmap-scanner"


def test_version_lock_candidate_from_documented_tool_is_needs_review() -> None:
    definition = ToolDefinition(
        tool_id="nmap",
        display_name="Nmap",
        category=DOCUMENTED_TOOL_CATEGORY,
        module_ids=("m01_osint",),
        runtime="documented_only",
        workspace_path="storage/workspaces/m01_osint/tools/nmap",
        approved_status="documented_planned",
        healthcheck_method="not_configured",
        execution_implied=False,
    )

    entry = create_needs_review_lock_from_tool_definition(definition, "m01_osint")

    assert entry.tool_id == "m01_osint/nmap"
    assert entry.tool_name == "Nmap"
    assert entry.module_id == "m01_osint"
    assert entry.recommended_version == VERSION_LOCK_RECOMMENDED_UNRESOLVED
    assert entry.runtime == RUNTIME_CUSTOM
    assert entry.status == VERSION_LOCK_STATUS_NEEDS_REVIEW


def test_runtime_for_tool_definition_maps_package_categories() -> None:
    definition = ToolDefinition(
        tool_id="requests",
        display_name="requests",
        category="python_package",
        module_ids=("m16_ops_quality",),
        runtime="python",
        workspace_path="storage/workspaces/m16_ops_quality/tools/requests",
        approved_status="documented_planned",
        healthcheck_method="import_check",
        expected_version="2.32.0",
        execution_implied=False,
    )

    assert runtime_for_tool_definition(definition) == RUNTIME_PYTHON
    assert create_needs_review_lock_from_tool_definition(definition).recommended_version == "2.32.0"
