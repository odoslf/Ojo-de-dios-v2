"""Shared helpers for deterministic technique evidence metadata."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import NAMESPACE_URL, uuid5


def utc_now_iso() -> str:
    """Return an aware UTC timestamp for evidence records."""
    return datetime.now(UTC).isoformat()


def stable_evidence_id(run_id: str, technique_id: str, suffix: str) -> str:
    """Build a deterministic evidence id for a run, technique and evidence suffix."""
    return f"ev-{uuid5(NAMESPACE_URL, f'{run_id}:{technique_id}:{suffix}')}"
