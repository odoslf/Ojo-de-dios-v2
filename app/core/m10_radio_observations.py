"""M10 passive radio observation evidence; no RF transmission or capture is initiated."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M10_MODULE_ID = "m10_wireless_rf"
VALID_PROTOCOLS = frozenset({"wifi", "bluetooth", "ble", "rfid", "nfc", "zigbee", "z_wave", "sub_ghz", "other"})


@dataclass(frozen=True, slots=True)
class RadioObservation:
    """Metadata from an already observed radio signal or device, never an instruction to transmit."""

    protocol: str
    frequency_mhz: float | None
    label: str
    signal_dbm: float | None
    source: str
    observed_at: str

    def to_dict(self) -> dict[str, object]:
        return {"protocol": self.protocol, "frequency_mhz": self.frequency_mhz, "label": self.label, "signal_dbm": self.signal_dbm, "source": self.source, "observed_at": self.observed_at, "rf_capture_started_by_application": False, "rf_transmission_performed": False}


def radio_observation_from_payload(payload: dict[str, Any]) -> RadioObservation:
    """Validate supplied passive observation metadata."""
    protocol = str(payload.get("protocol", "")).strip().casefold()
    label = str(payload.get("label", "")).strip()
    source = str(payload.get("source", "operator_observed")).strip()
    observed_at = str(payload.get("observed_at", "")).strip()
    if protocol not in VALID_PROTOCOLS or not label or len(label) > 512 or not source or len(source) > 512 or not observed_at or len(observed_at) > 128:
        raise ValueError("protocol, label, source or observed_at is invalid.")
    frequency_raw = payload.get("frequency_mhz")
    try:
        frequency = float(frequency_raw) if frequency_raw is not None else None
        signal_raw = payload.get("signal_dbm")
        signal = float(signal_raw) if signal_raw is not None else None
    except (TypeError, ValueError) as exc:
        raise ValueError("frequency_mhz and signal_dbm must be numeric when supplied.") from exc
    if frequency is not None and not 0 < frequency <= 300_000:
        raise ValueError("frequency_mhz is outside accepted bounds.")
    if signal is not None and not -200 <= signal <= 100:
        raise ValueError("signal_dbm is outside accepted bounds.")
    return RadioObservation(protocol, frequency, label, signal, source, observed_at)


def write_m10_radio_observations(target: TargetRecord, observations: list[RadioObservation], repo_root: Path | None = None) -> Path:
    """Persist supplied passive radio observations in M10 target workspace."""
    if not observations or len(observations) > 10_000:
        raise ValueError("observation count must be between 1 and 10000.")
    root = Path.cwd() if repo_root is None else repo_root
    path = bind_target_module_workspace(target, M10_MODULE_ID, repo_root=root).root_path / "evidence" / "radio_observations.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema_version": 1, "target_id": target.target_id, "module_id": M10_MODULE_ID, "recorded_at": datetime.now(timezone.utc).isoformat(), "observations": [item.to_dict() for item in observations], "observation_count": len(observations), "rf_capture_started_by_application": False, "rf_transmission_performed": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_m10_radio_observations(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object] | None:
    """Read M10 observation evidence without using RF hardware."""
    root = Path.cwd() if repo_root is None else repo_root
    path = bind_target_module_workspace(target, M10_MODULE_ID, repo_root=root).root_path / "evidence" / "radio_observations.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None
