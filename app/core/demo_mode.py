"""Demo mode contract helpers."""

from dataclasses import dataclass

from app.core.errors import ContractError

DEMO_MODE_OFF = "off"
DEMO_MODE_ON = "on"

VALID_DEMO_MODES = {
    DEMO_MODE_OFF,
    DEMO_MODE_ON,
}


@dataclass
class DemoModeStatus:
    """Current demo mode status description."""

    enabled: bool
    mode: str
    message: str


def is_valid_demo_mode(mode: str) -> bool:
    """Return whether a demo mode value is supported."""
    return mode in VALID_DEMO_MODES


def get_demo_mode_status(enabled: bool) -> DemoModeStatus:
    """Return a normalized demo mode status."""
    if enabled:
        return DemoModeStatus(enabled=True, mode=DEMO_MODE_ON, message="Demo mode is enabled.")
    return DemoModeStatus(enabled=False, mode=DEMO_MODE_OFF, message="Demo mode is disabled.")


def ensure_demo_allowed(can_run_in_demo: bool) -> None:
    """Ensure a technique is allowed to run through demo fixtures."""
    if not can_run_in_demo:
        raise ContractError("Technique is not allowed to run in demo mode.")
