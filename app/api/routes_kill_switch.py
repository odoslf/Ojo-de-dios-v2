"""Kill switch API routes."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.kill_switch import (
    KillSwitchStatus,
    activate_kill_switch,
    get_kill_switch_status,
    reset_kill_switch,
)

router = APIRouter()


class KillSwitchActivateRequest(BaseModel):
    """Payload for activating the kill switch."""

    reason: str = "Global stop requested."
    activated_by: str | None = None


def _status_to_payload(status: KillSwitchStatus) -> dict[str, str | bool | None]:
    return {
        "status": status.status,
        "active": status.active,
        "reason": status.reason,
        "activated_by": status.activated_by,
        "activated_at": status.activated_at,
        "reset_at": status.reset_at,
    }


@router.get("/api/kill-switch/status")
def kill_switch_status() -> dict[str, str | bool | None]:
    """Return the current kill switch status."""
    return _status_to_payload(get_kill_switch_status())


@router.post("/api/kill-switch/activate")
def activate(payload: KillSwitchActivateRequest | None = None) -> dict[str, str | bool | None]:
    """Activate the kill switch."""
    request = payload or KillSwitchActivateRequest()
    return _status_to_payload(activate_kill_switch(request.reason, request.activated_by))


@router.post("/api/kill-switch/reset")
def reset() -> dict[str, str | bool | None]:
    """Reset the kill switch."""
    return _status_to_payload(reset_kill_switch())
