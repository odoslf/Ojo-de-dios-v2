"""Runtime state snapshot without workers or execution control."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RuntimeState:
    """Minimal runtime state reported by the router."""

    app_started_at: str
    kill_switch_active: bool = False
    active_jobs: int = 0
    notes: dict[str, str] = field(default_factory=dict)


def create_runtime_state() -> RuntimeState:
    """Create a local runtime state snapshot."""
    return RuntimeState(app_started_at=datetime.now(timezone.utc).isoformat())
