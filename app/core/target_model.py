"""Target model contract for Ojo de Dios."""

from dataclasses import dataclass, field
from typing import Any

from app.core.errors import ContractError

TARGET_DOMAIN = "domain"
TARGET_IP = "ip"
TARGET_RANGE = "range"
TARGET_URL = "url"
TARGET_EMAIL = "email"
TARGET_PERSON = "person"
TARGET_COMPANY = "company"
TARGET_ANDROID_DEVICE = "android_device"
TARGET_HACKRF_SESSION = "hackrf_session"
TARGET_BLUETOOTH_DEVICE = "bluetooth_device"
TARGET_WIFI_NETWORK = "wifi_network"
TARGET_CLOUD_ACCOUNT = "cloud_account"
TARGET_KUBERNETES_CLUSTER = "kubernetes_cluster"
TARGET_DOCKER_HOST = "docker_host"
TARGET_REPOSITORY = "repository"
TARGET_SCRAPING_QUERY = "scraping_query"
TARGET_IOT_DEVICE = "iot_device"
TARGET_CUSTOM = "custom"

VALID_TARGET_TYPES = {
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

TARGET_MODE_DEMO = "demo"
TARGET_MODE_DRY_RUN = "dry_run"
TARGET_MODE_CONTROLLED = "controlled"
TARGET_MODE_EXPERT = "expert"

VALID_TARGET_MODES = {
    TARGET_MODE_DEMO,
    TARGET_MODE_DRY_RUN,
    TARGET_MODE_CONTROLLED,
    TARGET_MODE_EXPERT,
}


@dataclass
class TargetRequest:
    """Request data required to define a target."""

    name: str
    target_type: str
    value: str
    mode: str = TARGET_MODE_DRY_RUN
    allowed_modules: list[str] = field(default_factory=list)
    limits: dict[str, Any] = field(default_factory=dict)
    noise_profile: str = "normal"
    evidence_profile: str = "standard"
    require_confirmations: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TargetRecord:
    """Stored target record contract."""

    target_id: str
    name: str
    target_type: str
    value: str
    normalized_value: str
    mode: str
    allowed_modules: list[str] = field(default_factory=list)
    limits: dict[str, Any] = field(default_factory=dict)
    noise_profile: str = "normal"
    evidence_profile: str = "standard"
    require_confirmations: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    created_by: str | None = None
    created_at: str | None = None


def is_valid_target_type(target_type: str) -> bool:
    """Return whether a target type is officially supported."""
    return target_type in VALID_TARGET_TYPES


def is_valid_target_mode(mode: str) -> bool:
    """Return whether a target mode is officially supported."""
    return mode in VALID_TARGET_MODES


def validate_target_request(request: TargetRequest) -> None:
    """Validate a target creation request without performing side effects."""
    if not request.name or not request.name.strip():
        raise ContractError("Target name cannot be empty.")
    if not is_valid_target_type(request.target_type):
        raise ContractError(f"Invalid target type: {request.target_type}")
    if not request.value or not request.value.strip():
        raise ContractError("Target value cannot be empty.")
    if not is_valid_target_mode(request.mode):
        raise ContractError(f"Invalid target mode: {request.mode}")
    if not isinstance(request.allowed_modules, list):
        raise ContractError("allowed_modules must be a list.")
    for module_id in request.allowed_modules:
        if not isinstance(module_id, str) or not module_id.strip():
            raise ContractError("allowed_modules entries must be non-empty strings.")
    if not isinstance(request.limits, dict):
        raise ContractError("limits must be a dict.")
    if not isinstance(request.metadata, dict):
        raise ContractError("metadata must be a dict.")
