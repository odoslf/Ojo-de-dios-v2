"""Secure secret-store contracts."""

import types

from app.core.secret_store import SecureSecretStore
from app.modules.m01_osint import techniques


def test_secret_store_reports_missing_tool_without_plaintext_file(monkeypatch) -> None:
    store = SecureSecretStore()
    monkeypatch.setenv("OJO_DISABLE_KEYRING", "1")
    monkeypatch.delenv("SHODAN_API_KEY", raising=False)

    result = store.get_secret("SHODAN_API_KEY", ("SHODAN_API_KEY",))

    assert result.status == "missing-tool"
    assert result.value is None


def test_secret_store_reads_from_keyring_backend_without_env(monkeypatch) -> None:
    calls = {"service": None, "name": None}

    def fake_import_module(name: str):
        assert name == "keyring"
        return types.SimpleNamespace(
            get_password=lambda service, secret_name: calls.update({"service": service, "name": secret_name}) or "secret-value",
        )

    monkeypatch.delenv("OJO_DISABLE_KEYRING", raising=False)
    monkeypatch.setattr("app.core.secret_store.importlib.import_module", fake_import_module)

    result = SecureSecretStore().get_secret("shodan_api_key", ("SHODAN_API_KEY",))

    assert result.status == "available"
    assert result.value == "secret-value"
    assert result.source == "keyring"
    assert calls == {"service": "ojo-de-dios", "name": "SHODAN_API_KEY"}


def test_m01_api_key_rejects_inline_plaintext_parameter() -> None:
    try:
        techniques._api_key({"api_key": "plaintext"}, ("SHODAN_API_KEY",))
    except Exception as error:
        assert "not inline parameters" in str(error)
    else:
        raise AssertionError("Expected inline plaintext API key to be rejected.")
