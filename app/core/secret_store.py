"""Secure secret lookup backed by the operating-system keyring when available."""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass

from app.core.errors import ContractError

SERVICE_PREFIX = "ojo-de-dios"


@dataclass(frozen=True, slots=True)
class SecretLookupResult:
    """Result of trying to read a secret without exposing the secret in logs."""

    status: str
    value: str | None = None
    source: str | None = None
    detail: str | None = None


class SecureSecretStore:
    """Retrieve and store secrets without writing plaintext into this repo/storage tree.

    The preferred backend is the Python ``keyring`` package, which delegates
    storage to the OS credential vault. Environment variables are allowed as a
    process-level runtime source for developer/CI usage, but this class never
    persists their values and never serializes secret material.
    """

    def __init__(self, service_prefix: str = SERVICE_PREFIX) -> None:
        self.service_prefix = service_prefix

    def get_secret(self, secret_name: str, env_names: tuple[str, ...] = ()) -> SecretLookupResult:
        normalized_name = self._normalize_name(secret_name)
        keyring_value = self._get_keyring_secret(normalized_name)
        if keyring_value.status == "available":
            return keyring_value
        for env_name in env_names:
            value = os.environ.get(env_name, "").strip()
            if value:
                return SecretLookupResult(status="available", value=value, source=f"env:{env_name}")
        if keyring_value.status == "missing-tool":
            return SecretLookupResult(
                status="missing-tool",
                source="keyring",
                detail="Install and configure the keyring package/backend or provide a runtime environment variable.",
            )
        return SecretLookupResult(status="missing-config", source="secure-secret-store", detail=f"Secret {normalized_name} is not configured.")

    def set_secret(self, secret_name: str, value: str) -> SecretLookupResult:
        normalized_name = self._normalize_name(secret_name)
        secret_value = value.strip()
        if not secret_value:
            raise ContractError("Secret value must be non-empty.")
        keyring_module = self._keyring_module()
        if keyring_module is None:
            return SecretLookupResult(status="missing-tool", source="keyring", detail="Python keyring package/backend is not installed.")
        keyring_module.set_password(self.service_prefix, normalized_name, secret_value)
        return SecretLookupResult(status="stored", source="keyring")

    def _get_keyring_secret(self, normalized_name: str) -> SecretLookupResult:
        keyring_module = self._keyring_module()
        if keyring_module is None:
            return SecretLookupResult(status="missing-tool", source="keyring")
        value = keyring_module.get_password(self.service_prefix, normalized_name)
        if value:
            return SecretLookupResult(status="available", value=str(value), source="keyring")
        return SecretLookupResult(status="missing-config", source="keyring")

    def _keyring_module(self):
        if os.environ.get("OJO_DISABLE_KEYRING", "").strip().lower() in {"1", "true", "yes", "on"}:
            return None
        try:
            return importlib.import_module("keyring")
        except ImportError:
            return None

    def _normalize_name(self, secret_name: str) -> str:
        normalized = secret_name.strip().upper()
        if not normalized:
            raise ContractError("Secret name must be non-empty.")
        allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        if any(char not in allowed for char in normalized):
            raise ContractError("Secret name contains unsupported characters.")
        return normalized


DEFAULT_SECRET_STORE = SecureSecretStore()
