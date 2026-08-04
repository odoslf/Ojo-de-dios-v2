"""M15 cloud, container, and Kubernetes inventory normalization."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M15_MODULE_ID = "m15_cloud"
MAX_ASSETS = 10_000
MAX_ATTRIBUTES = 100
MAX_ATTRIBUTE_DEPTH = 4
MAX_TEXT_LENGTH = 1_024
VALID_PROVIDERS = frozenset({"aws", "azure", "gcp", "kubernetes", "container", "other"})
VALID_EXPOSURES = frozenset({"private", "internal", "public", "unknown"})
_SENSITIVE_KEY_PARTS = ("secret", "password", "token", "credential", "private_key", "access_key")


def _text(value: object, name: str, *, max_length: int = MAX_TEXT_LENGTH, required: bool = True) -> str | None:
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{name} is required.")
        return None
    if len(text) > max_length or any(character in text for character in "\x00\r\n"):
        raise ValueError(f"{name} is invalid or too long.")
    return text


def _sanitize_attributes(value: object, depth: int = 0) -> tuple[object, int]:
    """Make imported metadata JSON-safe while removing embedded credential fields."""
    if depth > MAX_ATTRIBUTE_DEPTH:
        raise ValueError("attributes exceed the maximum nesting depth.")
    if isinstance(value, dict):
        if len(value) > MAX_ATTRIBUTES:
            raise ValueError(f"attributes may contain at most {MAX_ATTRIBUTES} keys per object.")
        cleaned: dict[str, object] = {}
        redacted = 0
        for raw_key, raw_value in value.items():
            key = _text(raw_key, "attribute key", max_length=128)
            if key is None:
                continue
            if any(part in key.casefold() for part in _SENSITIVE_KEY_PARTS):
                redacted += 1
                continue
            sanitized, nested_redacted = _sanitize_attributes(raw_value, depth + 1)
            cleaned[key] = sanitized
            redacted += nested_redacted
        return cleaned, redacted
    if isinstance(value, list):
        if len(value) > MAX_ATTRIBUTES:
            raise ValueError(f"attribute arrays may contain at most {MAX_ATTRIBUTES} values.")
        cleaned_items: list[object] = []
        redacted = 0
        for item in value:
            sanitized, nested_redacted = _sanitize_attributes(item, depth + 1)
            cleaned_items.append(sanitized)
            redacted += nested_redacted
        return cleaned_items, redacted
    if value is None or isinstance(value, (bool, int, float)):
        return value, 0
    return _text(value, "attribute value", max_length=MAX_TEXT_LENGTH) or "", 0


@dataclass(frozen=True, slots=True)
class CloudAsset:
    """Normalized inventory record from an existing cloud or cluster export."""

    provider: str
    resource_type: str
    resource_id: str
    region: str | None
    account_ref: str | None
    exposure: str
    state: str | None
    attributes: dict[str, object]
    redacted_attribute_count: int

    def to_dict(self) -> dict[str, object]:
        identity = f"{self.provider}\n{self.resource_type}\n{self.resource_id}\n{self.region or ''}\n{self.account_ref or ''}"
        return {
            "asset_id": hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16],
            "provider": self.provider,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "region": self.region,
            "account_ref": self.account_ref,
            "exposure": self.exposure,
            "state": self.state,
            "attributes": self.attributes,
            "redacted_attribute_count": self.redacted_attribute_count,
            "remote_collection_performed": False,
        }


def cloud_asset_from_payload(payload: dict[str, Any]) -> CloudAsset:
    """Validate one imported cloud, container, or Kubernetes asset record."""
    provider = (_text(payload.get("provider"), "provider") or "").casefold()
    exposure = (_text(payload.get("exposure", "unknown"), "exposure") or "").casefold()
    if provider not in VALID_PROVIDERS:
        raise ValueError("provider is invalid.")
    if exposure not in VALID_EXPOSURES:
        raise ValueError("exposure is invalid.")
    raw_attributes = payload.get("attributes", {})
    if not isinstance(raw_attributes, dict):
        raise ValueError("attributes must be an object.")
    attributes, redacted = _sanitize_attributes(raw_attributes)
    if not isinstance(attributes, dict):
        raise ValueError("attributes must normalize to an object.")
    return CloudAsset(
        provider=provider,
        resource_type=_text(payload.get("resource_type"), "resource_type") or "",
        resource_id=_text(payload.get("resource_id"), "resource_id") or "",
        region=_text(payload.get("region"), "region", required=False),
        account_ref=_text(payload.get("account_ref"), "account_ref", required=False),
        exposure=exposure,
        state=_text(payload.get("state"), "state", required=False),
        attributes=attributes,
        redacted_attribute_count=redacted,
    )


def summarize_cloud_assets(assets: list[CloudAsset]) -> dict[str, object]:
    """Build deterministic cloud inventory counts from imported records."""
    by_provider = Counter(asset.provider for asset in assets)
    by_exposure = Counter(asset.exposure for asset in assets)
    public_assets = [asset.to_dict() for asset in assets if asset.exposure == "public"]
    return {
        "asset_count": len(assets),
        "asset_count_by_provider": dict(sorted(by_provider.items())),
        "asset_count_by_exposure": dict(sorted(by_exposure.items())),
        "public_asset_count": len(public_assets),
        "public_asset_refs": [asset["asset_id"] for asset in public_assets],
        "redacted_attribute_count": sum(asset.redacted_attribute_count for asset in assets),
    }


def write_m15_cloud_inventory(target: TargetRecord, assets: list[CloudAsset], repo_root: Path | None = None) -> Path:
    """Persist a deduplicated inventory imported from an existing cloud export."""
    if not assets or len(assets) > MAX_ASSETS:
        raise ValueError(f"asset count must be between 1 and {MAX_ASSETS}.")
    unique = {asset.to_dict()["asset_id"]: asset.to_dict() for asset in assets}
    root = Path.cwd() if repo_root is None else repo_root
    path = bind_target_module_workspace(target, M15_MODULE_ID, repo_root=root).root_path / "evidence" / "cloud_inventory.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema_version": 1,
        "target_id": target.target_id,
        "module_id": M15_MODULE_ID,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "assets": list(unique.values()),
        "input_asset_count": len(assets),
        "deduplicated_asset_count": len(unique),
        "summary": summarize_cloud_assets(assets),
        "remote_collection_performed": False,
        "mutation_performed": False,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_m15_cloud_inventory(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object] | None:
    """Read the persisted M15 cloud inventory."""
    root = Path.cwd() if repo_root is None else repo_root
    path = bind_target_module_workspace(target, M15_MODULE_ID, repo_root=root).root_path / "evidence" / "cloud_inventory.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None
