"""Target normalization and fingerprint contracts."""

from dataclasses import dataclass, field
from ipaddress import ip_address, ip_network
import re
from typing import Any
from urllib.parse import urlparse

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
    TARGET_PERSON,
    TARGET_RANGE,
    TARGET_REPOSITORY,
    TARGET_SCRAPING_QUERY,
    TARGET_URL,
)

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_STRIP_ONLY_TARGETS = {
    TARGET_ANDROID_DEVICE,
    TARGET_BLUETOOTH_DEVICE,
    TARGET_CLOUD_ACCOUNT,
    TARGET_COMPANY,
    TARGET_CUSTOM,
    TARGET_DOCKER_HOST,
    TARGET_HACKRF_SESSION,
    TARGET_IOT_DEVICE,
    TARGET_KUBERNETES_CLUSTER,
    TARGET_PERSON,
}


@dataclass
class TargetFingerprint:
    """Deterministic, local fingerprint for a target."""

    target_id: str
    target_type: str
    original_value: str
    normalized_value: str
    fingerprint: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    confidence: float = 1.0


def _normalize_domain(value: str) -> str:
    stripped = value.strip().lower()
    if stripped.startswith(("http://", "https://")):
        parsed = urlparse(stripped)
        stripped = parsed.netloc
    else:
        stripped = stripped.split("/", 1)[0]
    if ":" in stripped:
        stripped = stripped.split(":", 1)[0]
    return stripped


def _normalize_url(value: str) -> str:
    parsed = urlparse(value.strip())
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"} or not parsed.netloc:
        raise ContractError("URL targets require http or https scheme and host.")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ContractError("URL targets require a host.")
    port = f":{parsed.port}" if parsed.port else ""
    path = parsed.path or ""
    return f"{scheme}://{host}{port}{path}"


def _normalize_email(value: str) -> str:
    normalized = value.strip().lower()
    if not _EMAIL_PATTERN.match(normalized):
        raise ContractError("Invalid email target value.")
    return normalized


def normalize_target_value(target_type: str, value: str) -> str:
    """Normalize a target value using only local deterministic parsing."""
    if target_type == TARGET_DOMAIN:
        return _normalize_domain(value)
    if target_type == TARGET_IP:
        try:
            return str(ip_address(value.strip()))
        except ValueError as exc:
            raise ContractError("Invalid IP target value.") from exc
    if target_type == TARGET_RANGE:
        try:
            return str(ip_network(value.strip(), strict=False))
        except ValueError as exc:
            raise ContractError("Invalid IP range target value.") from exc
    if target_type == TARGET_URL:
        return _normalize_url(value)
    if target_type == TARGET_EMAIL:
        return _normalize_email(value)
    if target_type == TARGET_REPOSITORY:
        return value.strip()
    if target_type == TARGET_SCRAPING_QUERY:
        return value.strip()
    if target_type in _STRIP_ONLY_TARGETS:
        return value.strip()
    return value.strip()


def build_target_fingerprint(target_id: str, target_type: str, value: str) -> TargetFingerprint:
    """Build a deterministic local fingerprint for a target."""
    normalized = normalize_target_value(target_type, value)
    if target_type == TARGET_DOMAIN:
        fingerprint = {"kind": "domain", "domain": normalized}
        tags = ["domain"]
    elif target_type == TARGET_IP:
        fingerprint = {"kind": "ip", "ip": normalized}
        tags = ["ip"]
    elif target_type == TARGET_RANGE:
        fingerprint = {"kind": "range", "cidr": normalized}
        tags = ["range"]
    elif target_type == TARGET_URL:
        parsed = urlparse(normalized)
        fingerprint = {
            "kind": "url",
            "url": normalized,
            "scheme": parsed.scheme,
            "host": parsed.hostname or "",
            "port": parsed.port,
            "path": parsed.path or "",
        }
        tags = ["url", "web"]
    elif target_type == TARGET_EMAIL:
        domain = normalized.rsplit("@", 1)[1]
        fingerprint = {"kind": "email", "email": normalized, "domain": domain}
        tags = ["email"]
    elif target_type == TARGET_SCRAPING_QUERY:
        fingerprint = {"kind": TARGET_SCRAPING_QUERY, "value": normalized}
        tags = ["scraping"]
    elif target_type == TARGET_REPOSITORY:
        fingerprint = {"kind": TARGET_REPOSITORY, "value": normalized}
        tags = ["repository"]
    else:
        fingerprint = {"kind": target_type, "value": normalized}
        tags = [target_type]
    return TargetFingerprint(
        target_id=target_id,
        target_type=target_type,
        original_value=value,
        normalized_value=normalized,
        fingerprint=fingerprint,
        tags=tags,
    )
