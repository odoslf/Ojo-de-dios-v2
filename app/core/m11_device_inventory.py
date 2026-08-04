"""M11 physical/IoT device inventory with privacy-preserving identifiers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M11_MODULE_ID = "m11_iot_physical"
VALID_DEVICE_TYPES = frozenset({"camera", "printer", "router", "sensor", "controller", "door_access", "domotics", "industrial", "other"})
VALID_OBSERVATION_STATES = frozenset({"observed", "offline", "maintenance", "retired"})


@dataclass(frozen=True, slots=True)
class DeviceObservation:
    """A physical-device observation with an irreversible identifier fingerprint."""

    device_type: str
    label: str
    identifier_sha256: str
    manufacturer: str | None
    model: str | None
    state: str
    source: str
    observed_at: str

    def to_dict(self) -> dict[str, object]:
        return {
            "device_type": self.device_type,
            "label": self.label,
            "identifier_sha256": self.identifier_sha256,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "state": self.state,
            "source": self.source,
            "observed_at": self.observed_at,
            "raw_identifier_persisted": False,
            "device_interaction_performed": False,
        }


def _bounded(value: object, name: str, required: bool = True) -> str | None:
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{name} is required.")
        return None
    if len(text) > 512 or "\x00" in text or "\r" in text or "\n" in text:
        raise ValueError(f"{name} is invalid or too long.")
    return text


def device_observation_from_payload(payload: dict[str, Any]) -> DeviceObservation:
    """Validate transient device identifier data and retain only its SHA-256 fingerprint."""
    device_type = str(payload.get("device_type", "")).strip().casefold()
    state = str(payload.get("state", "observed")).strip().casefold()
    if device_type not in VALID_DEVICE_TYPES or state not in VALID_OBSERVATION_STATES:
        raise ValueError("device_type or state is invalid.")
    identifier = _bounded(payload.get("device_identifier"), "device_identifier")
    return DeviceObservation(
        device_type=device_type,
        label=_bounded(payload.get("label"), "label") or "",
        identifier_sha256=hashlib.sha256((identifier or "").encode("utf-8")).hexdigest(),
        manufacturer=_bounded(payload.get("manufacturer"), "manufacturer", required=False),
        model=_bounded(payload.get("model"), "model", required=False),
        state=state,
        source=_bounded(payload.get("source", "operator_observed"), "source") or "operator_observed",
        observed_at=_bounded(payload.get("observed_at"), "observed_at") or "",
    )


def write_m11_device_inventory(target: TargetRecord, observations: list[DeviceObservation], repo_root: Path | None = None) -> Path:
    """Persist secret-free device observations without querying, pairing or controlling any device."""
    if not observations or len(observations) > 10_000:
        raise ValueError("observation count must be between 1 and 10000.")
    root = Path.cwd() if repo_root is None else repo_root
    path = bind_target_module_workspace(target, M11_MODULE_ID, repo_root=root).root_path / "evidence" / "device_inventory.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    unique = {item.identifier_sha256: item.to_dict() for item in observations}
    path.write_text(json.dumps({"schema_version": 1, "target_id": target.target_id, "module_id": M11_MODULE_ID, "recorded_at": datetime.now(timezone.utc).isoformat(), "devices": list(unique.values()), "input_observation_count": len(observations), "deduplicated_device_count": len(unique), "device_interaction_performed": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_m11_device_inventory(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object] | None:
    """Read M11 inventory without interacting with physical devices."""
    root = Path.cwd() if repo_root is None else repo_root
    path = bind_target_module_workspace(target, M11_MODULE_ID, repo_root=root).root_path / "evidence" / "device_inventory.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None
