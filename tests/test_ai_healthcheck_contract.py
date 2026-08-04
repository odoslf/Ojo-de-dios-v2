"""AI healthcheck contract tests."""

from app.ai.healthcheck import check_ai_health


def test_ai_health_disabled() -> None:
    status = check_ai_health(enabled=False, backend="ollama", model="CognitiveComputations/dolphin-mistral-nemo:12b", base_url="")

    assert status.status == "disabled"
    assert status.configured is False
    assert status.message == "AI is disabled."


def test_ai_health_unsupported_backend() -> None:
    status = check_ai_health(enabled=True, backend="unsupported", model="CognitiveComputations/dolphin-mistral-nemo:12b", base_url="local")

    assert status.status == "unsupported_backend"
    assert status.configured is False


def test_ai_health_missing_base_url() -> None:
    status = check_ai_health(enabled=True, backend="ollama", model="CognitiveComputations/dolphin-mistral-nemo:12b", base_url="")

    assert status.status == "missing_config"
    assert status.configured is False


def test_ai_health_configured_without_runtime_check() -> None:
    status = check_ai_health(
        enabled=True,
        backend="ollama",
        model="CognitiveComputations/dolphin-mistral-nemo:12b",
        base_url="http://127.0.0.1:11434",
    )

    assert status.status == "configured"
    assert status.configured is True
