"""M08 authorized resilience measurement evidence without generating load."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean
from typing import Any

from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M08_MODULE_ID = "m08_dos_resilience"
MAX_MEASUREMENTS = 10_000


@dataclass(frozen=True, slots=True)
class ResilienceMeasurement:
    """One externally observed measurement supplied by an approved monitoring source."""

    observed_at: str
    available: bool
    latency_ms: float | None
    source: str
    evidence_ref: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"observed_at": self.observed_at, "available": self.available, "latency_ms": self.latency_ms, "source": self.source, "evidence_ref": self.evidence_ref, "load_generated_by_application": False}


def measurement_from_payload(payload: dict[str, Any]) -> ResilienceMeasurement:
    """Validate an observed measurement; timestamps are retained as supplied evidence metadata."""
    observed_at = str(payload.get("observed_at", "")).strip()
    source = str(payload.get("source", "operator_observed")).strip()
    if not observed_at or len(observed_at) > 128 or not source or len(source) > 512:
        raise ValueError("observed_at and source are required and bounded.")
    available = payload.get("available")
    if not isinstance(available, bool):
        raise ValueError("available must be boolean.")
    latency_raw = payload.get("latency_ms")
    latency: float | None = None
    if latency_raw is not None:
        try:
            latency = float(latency_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("latency_ms must be numeric when supplied.") from exc
        if latency < 0 or latency > 86_400_000:
            raise ValueError("latency_ms is outside accepted bounds.")
    ref = str(payload.get("evidence_ref", "")).strip() or None
    return ResilienceMeasurement(observed_at=observed_at, available=available, latency_ms=latency, source=source, evidence_ref=ref)


def summarize_resilience(measurements: list[ResilienceMeasurement]) -> dict[str, object]:
    """Summarize supplied observations; it makes no availability claim beyond this sample."""
    total = len(measurements)
    available = sum(1 for item in measurements if item.available)
    latencies = [item.latency_ms for item in measurements if item.latency_ms is not None]
    return {
        "sample_count": total,
        "available_count": available,
        "unavailable_count": total - available,
        "availability_rate": available / total if total else 0.0,
        "latency_ms_average": fmean(latencies) if latencies else None,
        "latency_ms_max": max(latencies) if latencies else None,
        "interpretation": "Summary reflects supplied observations only; it is not a load-test result.",
    }


def write_m08_resilience_measurements(target: TargetRecord, measurements: list[ResilienceMeasurement], repo_root: Path | None = None) -> Path:
    """Persist authorized observed resilience measurements in the target M08 workspace."""
    if not measurements or len(measurements) > MAX_MEASUREMENTS:
        raise ValueError(f"measurement count must be between 1 and {MAX_MEASUREMENTS}.")
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M08_MODULE_ID, repo_root=root)
    path = binding.root_path / "evidence" / "resilience_measurements.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema_version": 1, "target_id": target.target_id, "module_id": M08_MODULE_ID, "recorded_at": datetime.now(timezone.utc).isoformat(), "measurements": [item.to_dict() for item in measurements], "summary": summarize_resilience(measurements), "load_generated_by_application": False, "target_activity_performed": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_m08_resilience_measurements(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object] | None:
    """Read stored M08 measurements without touching the target."""
    root = Path.cwd() if repo_root is None else repo_root
    path = bind_target_module_workspace(target, M08_MODULE_ID, repo_root=root).root_path / "evidence" / "resilience_measurements.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None
