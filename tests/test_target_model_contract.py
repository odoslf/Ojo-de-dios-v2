"""Contract tests for target model validation."""

import pytest

from app.core.errors import ContractError
from app.core.target_model import (
    TARGET_ANDROID_DEVICE,
    TARGET_BLUETOOTH_DEVICE,
    TARGET_CLOUD_ACCOUNT,
    TARGET_COMPANY,
    TARGET_CUSTOM,
    TARGET_DOCKER_HOST,
    TARGET_DOMAIN,
    TARGET_EMAIL,
    TARGET_HACKRF_SESSION,
    TARGET_IOT_DEVICE,
    TARGET_IP,
    TARGET_KUBERNETES_CLUSTER,
    TARGET_MODE_CONTROLLED,
    TARGET_MODE_DEMO,
    TARGET_MODE_DRY_RUN,
    TARGET_MODE_EXPERT,
    TARGET_PERSON,
    TARGET_RANGE,
    TARGET_REPOSITORY,
    TARGET_SCRAPING_QUERY,
    TARGET_URL,
    TARGET_WIFI_NETWORK,
    TargetRequest,
    is_valid_target_mode,
    is_valid_target_type,
    validate_target_request,
)


def test_official_target_types_are_valid() -> None:
    target_types = {
        TARGET_DOMAIN,
        TARGET_IP,
        TARGET_RANGE,
        TARGET_URL,
        TARGET_EMAIL,
        TARGET_PERSON,
        TARGET_COMPANY,
        TARGET_ANDROID_DEVICE,
        TARGET_HACKRF_SESSION,
        TARGET_BLUETOOTH_DEVICE,
        TARGET_WIFI_NETWORK,
        TARGET_CLOUD_ACCOUNT,
        TARGET_KUBERNETES_CLUSTER,
        TARGET_DOCKER_HOST,
        TARGET_REPOSITORY,
        TARGET_SCRAPING_QUERY,
        TARGET_IOT_DEVICE,
        TARGET_CUSTOM,
    }
    assert all(is_valid_target_type(target_type) for target_type in target_types)
    assert not is_valid_target_type("bad_type")


def test_official_target_modes_are_valid() -> None:
    modes = {TARGET_MODE_DEMO, TARGET_MODE_DRY_RUN, TARGET_MODE_CONTROLLED, TARGET_MODE_EXPERT}
    assert all(is_valid_target_mode(mode) for mode in modes)
    assert not is_valid_target_mode("bad_mode")


def test_valid_target_request_passes() -> None:
    request = TargetRequest(name="Example", target_type=TARGET_DOMAIN, value="example.com")
    validate_target_request(request)


def test_empty_name_raises_contract_error() -> None:
    request = TargetRequest(name=" ", target_type=TARGET_DOMAIN, value="example.com")
    with pytest.raises(ContractError):
        validate_target_request(request)


def test_invalid_target_type_raises_contract_error() -> None:
    request = TargetRequest(name="Example", target_type="bad_type", value="example.com")
    with pytest.raises(ContractError):
        validate_target_request(request)


def test_empty_value_raises_contract_error() -> None:
    request = TargetRequest(name="Example", target_type=TARGET_DOMAIN, value=" ")
    with pytest.raises(ContractError):
        validate_target_request(request)


def test_invalid_mode_raises_contract_error() -> None:
    request = TargetRequest(name="Example", target_type=TARGET_DOMAIN, value="example.com", mode="bad_mode")
    with pytest.raises(ContractError):
        validate_target_request(request)


def test_allowed_modules_entries_must_be_non_empty_strings() -> None:
    request = TargetRequest(
        name="Example",
        target_type=TARGET_DOMAIN,
        value="example.com",
        allowed_modules=["m01_osint", ""],
    )
    with pytest.raises(ContractError):
        validate_target_request(request)
