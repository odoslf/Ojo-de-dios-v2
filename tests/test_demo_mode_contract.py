"""Demo mode contract tests."""

import pytest

from app.core.demo_mode import ensure_demo_allowed, get_demo_mode_status, is_valid_demo_mode
from app.core.errors import ContractError


def test_demo_mode_on_is_valid() -> None:
    assert is_valid_demo_mode("on") is True


def test_demo_mode_off_is_valid() -> None:
    assert is_valid_demo_mode("off") is True


def test_demo_mode_bad_is_invalid() -> None:
    assert is_valid_demo_mode("bad") is False


def test_get_demo_mode_status_enabled() -> None:
    status = get_demo_mode_status(True)

    assert status.enabled is True
    assert status.mode == "on"


def test_get_demo_mode_status_disabled() -> None:
    status = get_demo_mode_status(False)

    assert status.enabled is False
    assert status.mode == "off"


def test_ensure_demo_allowed_accepts_true() -> None:
    ensure_demo_allowed(True)


def test_ensure_demo_allowed_rejects_false() -> None:
    with pytest.raises(ContractError):
        ensure_demo_allowed(False)
