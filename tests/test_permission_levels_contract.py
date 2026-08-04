"""Permission levels contract tests."""

import pytest

from app.core.errors import ContractError
from app.core.permission_levels import (
    CONFIRMATION_REQUIRED_PERMISSION_LEVELS,
    PERMISSION_ACTIVE_LOW,
    PERMISSION_ACTIVE_SENSITIVE,
    PERMISSION_CLOUD_MUTATION,
    PERMISSION_CREDENTIALS,
    PERMISSION_HARDWARE,
    PERMISSION_LAB_ONLY,
    PERMISSION_PASSIVE,
    PERMISSION_PERSISTENCE,
    PERMISSION_RF_TRANSMIT,
    VALID_PERMISSION_LEVELS,
    TechniquePermissionProfile,
    is_valid_permission_level,
    permission_level_requires_confirmation,
    validate_permission_profile,
)


def test_all_official_permissions_are_valid() -> None:
    official_permissions = {
        PERMISSION_PASSIVE,
        PERMISSION_ACTIVE_LOW,
        PERMISSION_ACTIVE_SENSITIVE,
        PERMISSION_HARDWARE,
        PERMISSION_RF_TRANSMIT,
        PERMISSION_CREDENTIALS,
        PERMISSION_CLOUD_MUTATION,
        PERMISSION_PERSISTENCE,
        PERMISSION_LAB_ONLY,
    }

    assert official_permissions == VALID_PERMISSION_LEVELS
    assert all(is_valid_permission_level(permission) for permission in official_permissions)
    assert not is_valid_permission_level("BAD_PERMISSION")


def test_confirmation_required_permissions() -> None:
    expected_confirmation_permissions = {
        PERMISSION_ACTIVE_SENSITIVE,
        PERMISSION_RF_TRANSMIT,
        PERMISSION_CREDENTIALS,
        PERMISSION_CLOUD_MUTATION,
        PERMISSION_PERSISTENCE,
    }

    assert expected_confirmation_permissions == CONFIRMATION_REQUIRED_PERMISSION_LEVELS
    assert all(
        permission_level_requires_confirmation(permission)
        for permission in expected_confirmation_permissions
    )
    assert not permission_level_requires_confirmation(PERMISSION_PASSIVE)


def test_validate_permission_profile_accepts_valid_passive_profile() -> None:
    profile = TechniquePermissionProfile(
        technique_id="passive-profile",
        permission_level=PERMISSION_PASSIVE,
    )

    validate_permission_profile(profile)


def test_validate_permission_profile_rejects_empty_technique_id() -> None:
    profile = TechniquePermissionProfile(
        technique_id="",
        permission_level=PERMISSION_PASSIVE,
    )

    with pytest.raises(ContractError):
        validate_permission_profile(profile)


def test_validate_permission_profile_rejects_invalid_permission_level() -> None:
    profile = TechniquePermissionProfile(
        technique_id="bad-permission-profile",
        permission_level="BAD_PERMISSION",
    )

    with pytest.raises(ContractError):
        validate_permission_profile(profile)


def test_validate_permission_profile_requires_confirmation_for_rf_transmit() -> None:
    profile = TechniquePermissionProfile(
        technique_id="rf-profile",
        permission_level=PERMISSION_RF_TRANSMIT,
        requires_confirmation=False,
    )

    with pytest.raises(ContractError):
        validate_permission_profile(profile)
