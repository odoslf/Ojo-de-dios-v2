"""Global kill switch for blocking new job starts."""

from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.errors import ContractError

KILL_SWITCH_INACTIVE = "inactive"
KILL_SWITCH_ACTIVE = "active"
KILL_SWITCH_RESET_REQUIRED = "reset_required"


@dataclass
class KillSwitchStatus:
    """Current kill switch state."""

    status: str
    active: bool
    reason: str = ""
    activated_by: str | None = None
    activated_at: str | None = None
    reset_at: str | None = None


class KillSwitchController:
    """In-memory controller for global job-start blocking."""

    def __init__(self) -> None:
        self._status = KillSwitchStatus(status=KILL_SWITCH_INACTIVE, active=False)

    def get_status(self) -> KillSwitchStatus:
        """Return the current kill switch status."""
        return KillSwitchStatus(
            status=self._status.status,
            active=self._status.active,
            reason=self._status.reason,
            activated_by=self._status.activated_by,
            activated_at=self._status.activated_at,
            reset_at=self._status.reset_at,
        )

    def activate(self, reason: str, activated_by: str | None = None) -> KillSwitchStatus:
        """Activate the kill switch and block new jobs."""
        normalized_reason = reason if reason else "Global stop requested."
        self._status = KillSwitchStatus(
            status=KILL_SWITCH_ACTIVE,
            active=True,
            reason=normalized_reason,
            activated_by=activated_by,
            activated_at=datetime.now(UTC).isoformat(),
            reset_at=None,
        )
        return self.get_status()

    def reset(self) -> KillSwitchStatus:
        """Reset the kill switch so new jobs may start again."""
        self._status = KillSwitchStatus(
            status=KILL_SWITCH_INACTIVE,
            active=False,
            reason="",
            activated_by=None,
            activated_at=None,
            reset_at=datetime.now(UTC).isoformat(),
        )
        return self.get_status()

    def ensure_can_start_job(self) -> None:
        """Raise when the kill switch blocks new job starts."""
        if self._status.active:
            raise ContractError("Kill switch active: new jobs are blocked.")


_global_kill_switch = KillSwitchController()


def get_global_kill_switch() -> KillSwitchController:
    """Return the process-global kill switch controller."""
    return _global_kill_switch


def get_kill_switch_status() -> KillSwitchStatus:
    """Return the process-global kill switch status."""
    return _global_kill_switch.get_status()


def activate_kill_switch(reason: str, activated_by: str | None = None) -> KillSwitchStatus:
    """Activate the process-global kill switch."""
    return _global_kill_switch.activate(reason, activated_by)


def reset_kill_switch() -> KillSwitchStatus:
    """Reset the process-global kill switch."""
    return _global_kill_switch.reset()
