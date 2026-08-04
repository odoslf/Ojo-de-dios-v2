"""Runtime configuration for Ojo de Dios."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import (
    DEFAULT_EXECUTION_MODE,
    PRODUCT_DISPLAY_NAME_DEFAULT,
    PRODUCT_INTERNAL_NAME_DEFAULT,
    APP_VERSION_DEFAULT,
    VALID_EXECUTION_MODES,
)
from app.core.errors import ConfigurationError


class Settings(BaseSettings):
    """Application settings loaded from the environment and optional .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    product_internal_name: str = PRODUCT_INTERNAL_NAME_DEFAULT
    product_display_name: str = PRODUCT_DISPLAY_NAME_DEFAULT
    app_version: str = APP_VERSION_DEFAULT
    app_env: str = "local"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    default_execution_mode: str = DEFAULT_EXECUTION_MODE
    auto_cleanup_enabled: bool = False
    evidence_retention_days: int = 90
    job_log_retention_days: int = 30
    hermes_evidence_retention_days: int = 180
    keep_failed_runs: bool = True
    keep_demo_runs: bool = True
    database_url: str = "sqlite:///./storage/runtime/ojo_de_dios.sqlite3"
    storage_root: str = "storage"
    runtime_storage_dir: str = "storage/runtime"
    workspaces_storage_dir: str = "storage/workspaces"
    evidence_storage_dir: str = "storage/evidence"
    job_logs_storage_dir: str = "storage/job_logs"
    reports_storage_dir: str = "storage/reports"
    temp_storage_dir: str = "storage/tmp"
    initial_admin_username: str = "admin"
    initial_admin_password: str = ""
    password_hash_iterations: int = 260000
    technique_registry_packages: str = "app.modules"
    api_rate_limit_enabled: bool = True
    api_rate_limit_requests: int = 120
    api_rate_limit_window_seconds: int = 60

    ai_enabled: bool = False
    ai_backend: str = "ollama"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ai_request_timeout_seconds: int = 30
    mistral_enabled: bool = False
    mistral_api_url: str = "http://localhost:11434"
    mistral_chat_api_url: str = "http://localhost:11434/api/chat"
    mistral_model: str = "CognitiveComputations/dolphin-mistral-nemo:12b"
    mistral_model_display_name: str = "Dolphin Mistral Nemo 12B"
    mistral_prompt_template: str = "chatml"
    mistral_context_window_tokens: int = 128_000
    mistral_guardrails_required: bool = True
    mistral_timeout_seconds: int = 120
    mistral_system_prompt_path: str = "docs/ai_prompts/laia_mistral_system_prompt.md"
    ollama_models: str = "storage/models/ollama"
    ollama_models_dir: str = "storage/models/ollama"
    laia_mode: str = "local"
    laia_json_only: bool = True
    angel_enabled: bool = False
    angel_internal_name: str = "hermes_lab"
    angel_display_name: str = "Hermes Agent Lab"
    angel_legacy_alias: str = ""
    angel_provider: str = "deepseek"
    deepseek_api_key: str = ""
    deepseek_api_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-pro"
    deepseek_fast_model: str = "deepseek-v4-flash"
    deepseek_pro_model: str = "deepseek-v4-pro"
    deepseek_allow_pro_without_explicit_approval: bool = False
    angel_workspace: str = "modules/laboratory"
    angel_prompt_path: str = "docs/ai_prompts/angel_hermes_system_prompt.md"
    angel_allow_dependency_install: bool = False
    angel_require_approval: bool = True
    angel_sandbox_only: bool = True
    angel_output_manifest: bool = True
    angel_proposal_manifest: str = "PROMOTION_MANIFEST.json"
    angel_promoted_manifest_dir: str = "modules/laboratory/_promoted_manifest"

    def sanitized_ai_settings(self) -> dict[str, object]:
        """Return AI/Hermes settings safe for logs, healthchecks and panels."""
        return {
            "ai_enabled": self.ai_enabled,
            "ai_backend": self.ai_backend,
            "ollama_base_url": self.ollama_base_url,
            "mistral_enabled": self.mistral_enabled if self.ai_enabled else False,
            "mistral_model": self.mistral_model,
            "mistral_model_display_name": self.mistral_model_display_name,
            "mistral_prompt_template": self.mistral_prompt_template,
            "mistral_context_window_tokens": self.mistral_context_window_tokens,
            "mistral_guardrails_required": self.mistral_guardrails_required,
            "mistral_system_prompt_path": self.mistral_system_prompt_path,
            "angel_enabled": self.angel_enabled if self.ai_enabled else False,
            "angel_internal_name": self.angel_internal_name,
            "angel_display_name": self.angel_display_name,
            "angel_provider": self.angel_provider,
            "deepseek_api_key": "set" if self.deepseek_api_key else "missing",
            "deepseek_api_url": self.deepseek_api_url,
            "deepseek_model": self.deepseek_model,
            "deepseek_fast_model": self.deepseek_fast_model,
            "deepseek_pro_model": self.deepseek_pro_model,
            "angel_workspace": self.angel_workspace,
            "angel_allow_dependency_install": self.angel_allow_dependency_install,
            "angel_require_approval": self.angel_require_approval,
            "angel_sandbox_only": self.angel_sandbox_only,
        }

    @field_validator("default_execution_mode")
    @classmethod
    def validate_default_execution_mode(cls, value: str) -> str:
        """Ensure the configured execution mode is supported."""
        if value not in VALID_EXECUTION_MODES:
            valid_modes = ", ".join(sorted(VALID_EXECUTION_MODES))
            raise ConfigurationError(
                f"Invalid default execution mode '{value}'. Valid modes: {valid_modes}."
            )
        return value

    @field_validator("ai_backend")
    @classmethod
    def validate_ai_backend(cls, value: str) -> str:
        """Ensure only supported local AI backends are configured."""
        if value != "ollama":
            raise ConfigurationError("AI_BACKEND must be 'ollama' until another backend is implemented.")
        return value

    @field_validator("mistral_model")
    @classmethod
    def validate_mistral_model(cls, value: str) -> str:
        """Pin the official Mistral model name used by the Windows station."""
        expected = "CognitiveComputations/dolphin-mistral-nemo:12b"
        if value != expected:
            raise ConfigurationError(f"MISTRAL_MODEL must be {expected!r}.")
        return value


    @field_validator("mistral_prompt_template")
    @classmethod
    def validate_mistral_prompt_template(cls, value: str) -> str:
        """Dolphin Mistral Nemo uses ChatML formatting under Ollama."""
        if value != "chatml":
            raise ConfigurationError("MISTRAL_PROMPT_TEMPLATE must be 'chatml'.")
        return value

    @field_validator("mistral_context_window_tokens")
    @classmethod
    def validate_mistral_context_window_tokens(cls, value: int) -> int:
        """Keep the configured context window aligned with Mistral Nemo capacity."""
        if value < 8192 or value > 128_000:
            raise ConfigurationError("MISTRAL_CONTEXT_WINDOW_TOKENS must be between 8192 and 128000.")
        return value

    @field_validator("deepseek_model")
    @classmethod
    def validate_deepseek_model(cls, value: str) -> str:
        """Keep DeepSeekAssist on configured DeepSeek policy models."""
        if value not in {"deepseek-v4-flash", "deepseek-v4-pro"}:
            raise ConfigurationError("DEEPSEEK_MODEL must be 'deepseek-v4-flash' or 'deepseek-v4-pro'.")
        return value

    @field_validator(
        "storage_root",
        "runtime_storage_dir",
        "workspaces_storage_dir",
        "evidence_storage_dir",
        "job_logs_storage_dir",
        "reports_storage_dir",
        "temp_storage_dir",
        "angel_workspace",
        "angel_prompt_path",
        "angel_promoted_manifest_dir",
    )
    @classmethod
    def validate_relative_paths(cls, value: str) -> str:
        """Keep repository-local paths relative for portability between Windows and Linux."""
        if not value or value.startswith(("/", "\\")) or ":" in value:
            raise ConfigurationError("Configured Ojo de Dios paths must be repository-relative.")
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
