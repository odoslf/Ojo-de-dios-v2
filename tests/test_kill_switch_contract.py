"""Kill switch controller contract tests."""

import pytest

from app.core.errors import ContractError
from app.core.kill_switch import KILL_SWITCH_INACTIVE, KillSwitchController


def test_kill_switch_controller_lifecycle() -> None:
    controller = KillSwitchController()

    initial = controller.get_status()
    assert initial.status == KILL_SWITCH_INACTIVE
    assert initial.active is False

    activated = controller.activate("test", "tester")
    assert activated.active is True

    status = controller.get_status()
    assert status.reason == "test"
    assert status.activated_by == "tester"

    with pytest.raises(ContractError):
        controller.ensure_can_start_job()

    reset = controller.reset()
    assert reset.status == KILL_SWITCH_INACTIVE
    assert reset.active is False

    controller.ensure_can_start_job()
