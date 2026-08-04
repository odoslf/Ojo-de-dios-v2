"""Manual implementation contract tests."""

from app.contracts.manual_required import ManualImplementationRequired


def test_manual_required_default_message_contains_marker() -> None:
    error = ManualImplementationRequired()

    assert "IMPLEMENTACION_USUARIO_REQUERIDA" in str(error)


def test_manual_required_custom_message_is_preserved() -> None:
    error = ManualImplementationRequired("custom message")

    assert str(error) == "custom message"


def test_manual_required_marker_constant() -> None:
    assert ManualImplementationRequired.marker == "IMPLEMENTACION_USUARIO_REQUERIDA"
