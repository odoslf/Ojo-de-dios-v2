"""M16 operational readiness checks.

These checks are intentionally local and non-invasive. They inspect repository
files, environment flags, and local executable availability without contacting
AI backends or external APIs. A missing optional AI station is reported honestly
as partial/missing, never as a fake success.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from app.contracts.evidence_contract import VALID_EVIDENCE_QUALITIES
from app.core.tool_health import ToolHealthSpec, check_tool_health
from app.core.tool_inventory import list_documented_tools_for_module
from app.core.version_lock import (
    RUNTIME_PYTHON,
    VERSION_LOCK_RECOMMENDED_UNRESOLVED,
    VERSION_LOCK_STATUS_LOCKED,
    VERSION_LOCK_STATUS_NEEDS_REVIEW,
    create_locked_entry,
    create_needs_review_lock_from_tool_definition,
)
from app.modules.registry import ModuleManifestError, validate_all_module_manifests

STATUS_READY_CONTROLLED = "READY_CONTROLLED"
STATUS_READY_LOCAL_AI = "READY_LOCAL_AI"
STATUS_LAB_WORKSPACE_READY = "LAB_WORKSPACE_READY"
STATUS_KNOWLEDGE_MISSING = "KNOWLEDGE_MISSING"
STATUS_KNOWLEDGE_STALE = "KNOWLEDGE_STALE"
STATUS_MODEL_MISSING = "MODEL_MISSING"
STATUS_MISSING_TOOL = "MISSING_TOOL"
STATUS_PARTIAL = "PARTIAL"
STATUS_FAILED = "FAILED"
STATUS_DISABLED = "DISABLED"

M16_MODULE_ID = "m16_ops_quality"
MISTRAL_OFFICIAL_MODEL = "CognitiveComputations/dolphin-mistral-nemo:12b"
RUNTIME_STATUS_FILENAME = "m16_readiness_status.json"
READINESS_HISTORY_FILENAME = "m16_readiness_history.jsonl"
READINESS_ALERTS_FILENAME = "m16_readiness_alerts.jsonl"
LAIA_MISTRAL_RUNTIME_STATUS_FILENAME = "laia_mistral_status.json"
ANGEL_HERMES_RUNTIME_STATUS_FILENAME = "angel_hermes_status.json"

EVIDENCE_REQUIRED_FIELDS = {
    "evidence_id",
    "run_id",
    "target_id",
    "technique_id",
    "module_id",
    "evidence_type",
    "quality",
    "summary",
    "source",
    "demo",
    "real_execution",
    "created_at",
}

SECRET_KEY_PATTERN = re.compile(r"(api[_-]?key|token|secret|password|passwd|credential)", re.IGNORECASE)
SECRET_VALUE_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{16,}"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[^'\"\s]{8,}"),
)
RUNTIME_CLEANUP_SUFFIXES = (".tmp", ".temp", ".bak", ".old")
RUNTIME_CLEANUP_PREFIXES = ("tmp_", "temp_")
M16_EXPORT_REQUIRED_PATHS = (
    "scripts/export_project_zip.py",
    "scripts/windows/exportar_ojo_de_dios_zip.bat",
    "docs/MANO_DE_DIOS_SEPARATION.md",
    "docs/EVIDENCE_CONTRACT.md",
)

SECRET_ENV_KEYS = {
    "DEEPSEEK_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "MISTRAL_API_KEY",
}


@dataclass(frozen=True, slots=True)
class M16ComponentStatus:
    """One checked M16 component."""

    name: str
    status: str
    message: str
    required: bool = True
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe component status."""
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "required": self.required,
            "details": self.details,
        }


@dataclass(frozen=True, slots=True)
class M16ReadinessReport:
    """M16 readiness snapshot."""

    module_id: str
    status: str
    generated_at: str
    components: tuple[M16ComponentStatus, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe readiness report."""
        return {
            "module_id": self.module_id,
            "status": self.status,
            "generated_at": self.generated_at,
            "components": [component.to_dict() for component in self.components],
        }



@dataclass(frozen=True, slots=True)
class M16ReadinessAlert:
    """One degraded-state alert derived from an M16 readiness report."""

    alert_id: str
    module_id: str
    severity: str
    status: str
    message: str
    generated_at: str
    component: str | None = None
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "alert_id": self.alert_id,
            "module_id": self.module_id,
            "severity": self.severity,
            "status": self.status,
            "message": self.message,
            "generated_at": self.generated_at,
            "component": self.component,
            "details": self.details,
        }


def _history_paths(runtime_dir: Path) -> tuple[Path, Path]:
    return runtime_dir / READINESS_HISTORY_FILENAME, runtime_dir / READINESS_ALERTS_FILENAME


def _alert_severity(status: str, required: bool) -> str:
    if status == STATUS_FAILED:
        return "critical" if required else "warning"
    if status in {STATUS_MISSING_TOOL, STATUS_MODEL_MISSING}:
        return "error" if required else "warning"
    if status in {STATUS_PARTIAL, STATUS_KNOWLEDGE_MISSING, STATUS_KNOWLEDGE_STALE, STATUS_DISABLED}:
        return "warning"
    return "info"


def build_m16_readiness_alerts(report: M16ReadinessReport) -> tuple[M16ReadinessAlert, ...]:
    """Build deterministic degraded-state alerts from a readiness report."""
    alerts: list[M16ReadinessAlert] = []
    generated_at = datetime.now(timezone.utc).isoformat()
    if report.status != STATUS_READY_CONTROLLED:
        problematic = [
            component
            for component in report.components
            if component.status not in {STATUS_READY_CONTROLLED, STATUS_READY_LOCAL_AI, STATUS_LAB_WORKSPACE_READY}
        ]
        alerts.append(
            M16ReadinessAlert(
                alert_id=f"m16-overall-{report.generated_at}",
                module_id=report.module_id,
                severity="critical" if report.status == STATUS_FAILED else "warning",
                status=report.status,
                message=f"M16 readiness is degraded: {report.status}.",
                generated_at=generated_at,
                details={"problematic_component_count": len(problematic)},
            )
        )
        for component in problematic:
            alerts.append(
                M16ReadinessAlert(
                    alert_id=f"m16-component-{component.name}-{report.generated_at}",
                    module_id=report.module_id,
                    severity=_alert_severity(component.status, component.required),
                    status=component.status,
                    message=component.message,
                    generated_at=generated_at,
                    component=component.name,
                    details={"required": component.required},
                )
            )
    return tuple(alerts)


def append_m16_readiness_history(report: M16ReadinessReport, runtime_dir: Path | None = None) -> dict[str, object]:
    """Persist one readiness observation and any degraded alerts to JSONL history files."""
    target_dir = Path("storage/runtime") if runtime_dir is None else runtime_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    history_path, alerts_path = _history_paths(target_dir)
    alerts = build_m16_readiness_alerts(report)
    observation = {
        "schema_version": "m16.readiness_history.v1",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "readiness": report.to_dict(),
        "alert_count": len(alerts),
    }
    with history_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(observation, ensure_ascii=False, sort_keys=True) + "\n")
    if alerts:
        with alerts_path.open("a", encoding="utf-8") as handle:
            for alert in alerts:
                handle.write(json.dumps(alert.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
    return {
        "history_path": history_path.as_posix(),
        "alerts_path": alerts_path.as_posix(),
        "alert_count": len(alerts),
        "alerts": [alert.to_dict() for alert in alerts],
    }


def _read_jsonl(path: Path, limit: int) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows[-max(1, min(limit, 500)):]


def read_m16_readiness_history(runtime_dir: Path | None = None, limit: int = 50) -> dict[str, object]:
    """Read persisted readiness observations and alert history."""
    target_dir = Path("storage/runtime") if runtime_dir is None else runtime_dir
    history_path, alerts_path = _history_paths(target_dir)
    history = _read_jsonl(history_path, limit)
    alerts = _read_jsonl(alerts_path, limit)
    return {
        "schema_version": "m16.readiness_history_view.v1",
        "history_path": history_path.as_posix(),
        "alerts_path": alerts_path.as_posix(),
        "history_count": len(history),
        "alert_count": len(alerts),
        "history": history,
        "alerts": alerts,
    }

def _env_enabled(env: Mapping[str, str], key: str) -> bool:
    return env.get(key, "0").strip() == "1"


def _safe_env_flag_details(env: Mapping[str, str], keys: tuple[str, ...]) -> dict[str, object]:
    """Return environment flag presence without exposing secret values."""
    details: dict[str, object] = {}
    for key in keys:
        if key in SECRET_ENV_KEYS:
            details[key.lower()] = "set" if env.get(key) else "missing"
        else:
            details[key] = env.get(key, "")
    return details


def _path_exists_component(name: str, path: Path, ready_status: str, missing_status: str) -> M16ComponentStatus:
    if path.exists():
        return M16ComponentStatus(
            name=name,
            status=ready_status,
            message=f"Path exists: {path.as_posix()}.",
            details={"path": path.as_posix()},
        )
    return M16ComponentStatus(
        name=name,
        status=missing_status,
        message=f"Missing path: {path.as_posix()}.",
        details={"path": path.as_posix()},
    )


def check_module_manifest_integrity() -> M16ComponentStatus:
    """Validate that all module manifests match the authoritative catalog."""
    try:
        validated = validate_all_module_manifests()
    except ModuleManifestError as error:
        return M16ComponentStatus(
            name="module_manifest_integrity",
            status=STATUS_FAILED,
            message=str(error),
        )
    return M16ComponentStatus(
        name="module_manifest_integrity",
        status=STATUS_READY_CONTROLLED,
        message="All module manifests match the authoritative module catalog.",
        details={"validated_modules": list(validated), "validated_count": len(validated)},
    )


def check_runtime_storage(repo_root: Path) -> M16ComponentStatus:
    """Check runtime storage path availability without deleting or mutating data."""
    runtime_dir = repo_root / "storage" / "runtime"
    if not runtime_dir.exists():
        return M16ComponentStatus(
            name="runtime_storage",
            status=STATUS_FAILED,
            message="Runtime storage directory is missing.",
            details={"path": runtime_dir.as_posix()},
        )
    if not os.access(runtime_dir, os.W_OK):
        return M16ComponentStatus(
            name="runtime_storage",
            status=STATUS_FAILED,
            message="Runtime storage directory is not writable.",
            details={"path": runtime_dir.as_posix()},
        )
    return M16ComponentStatus(
        name="runtime_storage",
        status=STATUS_READY_CONTROLLED,
        message="Runtime storage directory exists and is writable.",
        details={"path": runtime_dir.as_posix()},
    )


def check_workspace_root(repo_root: Path) -> M16ComponentStatus:
    """Check that the shared module workspace root exists for controlled runs."""
    workspace_root = repo_root / "storage" / "workspaces"
    if not workspace_root.exists():
        return M16ComponentStatus(
            name="module_workspace_root",
            status=STATUS_PARTIAL,
            message="Module workspace root is missing; module workspaces can be created on demand.",
            required=False,
            details={"path": workspace_root.as_posix()},
        )
    return M16ComponentStatus(
        name="module_workspace_root",
        status=STATUS_READY_CONTROLLED,
        message="Module workspace root exists for controlled workspace creation.",
        details={"path": workspace_root.as_posix()},
    )


def check_ai_prompts(repo_root: Path) -> M16ComponentStatus:
    """Check required local system prompt files for LaIA/Mistral and Hermes."""
    required_paths = (
        repo_root / "docs" / "ai_prompts" / "laia_mistral_system_prompt.md",
        repo_root / "docs" / "ai_prompts" / "angel_hermes_system_prompt.md",
    )
    missing = [path.as_posix() for path in required_paths if not path.is_file()]
    if missing:
        return M16ComponentStatus(
            name="ai_prompts",
            status=STATUS_FAILED,
            message="One or more required AI system prompt files are missing.",
            details={"missing": missing},
        )
    return M16ComponentStatus(
        name="ai_prompts",
        status=STATUS_READY_CONTROLLED,
        message="Required AI system prompt files are present.",
        details={"paths": [path.as_posix() for path in required_paths]},
    )


def check_knowledge_base(repo_root: Path) -> M16ComponentStatus:
    """Check local knowledge artifacts without building embeddings or calling APIs."""
    knowledge_dir = repo_root / "storage" / "knowledge"
    if not knowledge_dir.exists():
        return M16ComponentStatus(
            name="knowledge_base",
            status=STATUS_KNOWLEDGE_MISSING,
            message="Knowledge directory is missing.",
            required=False,
            details={"path": knowledge_dir.as_posix()},
        )
    knowledge_files = [path for path in knowledge_dir.rglob("*") if path.is_file() and path.name != ".gitkeep"]
    if not knowledge_files:
        return M16ComponentStatus(
            name="knowledge_base",
            status=STATUS_KNOWLEDGE_MISSING,
            message="Knowledge directory exists but contains no built knowledge artifacts.",
            required=False,
            details={"path": knowledge_dir.as_posix(), "artifact_count": 0},
        )
    status_path = knowledge_dir / "knowledge_status.json"
    if not status_path.is_file():
        return M16ComponentStatus(
            name="knowledge_base",
            status=STATUS_KNOWLEDGE_STALE,
            message="Legacy knowledge artifacts exist, but the auditable knowledge_status.json manifest is missing.",
            required=False,
            details={"path": knowledge_dir.as_posix(), "artifact_count": len(knowledge_files)},
        )
    try:
        payload = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return M16ComponentStatus(
            name="knowledge_base",
            status=STATUS_KNOWLEDGE_STALE,
            message="Knowledge status manifest is unreadable.",
            required=False,
            details={
                "path": knowledge_dir.as_posix(),
                "status_path": status_path.as_posix(),
                "artifact_count": len(knowledge_files),
                "error": str(error),
            },
        )

    knowledge_status = str(payload.get("status", "UNKNOWN"))
    if knowledge_status not in {"READY_DOCS_ONLY", "READY_RAG"}:
        return M16ComponentStatus(
            name="knowledge_base",
            status=STATUS_KNOWLEDGE_STALE,
            message="Knowledge status manifest is present but does not report a ready knowledge base.",
            required=False,
            details={
                "path": knowledge_dir.as_posix(),
                "status_path": status_path.as_posix(),
                "knowledge_status": knowledge_status,
                "artifact_count": len(knowledge_files),
            },
        )
    return M16ComponentStatus(
        name="knowledge_base",
        status=STATUS_READY_LOCAL_AI,
        message="Auditable local knowledge artifacts are present.",
        required=False,
        details={
            "path": knowledge_dir.as_posix(),
            "status_path": status_path.as_posix(),
            "knowledge_status": knowledge_status,
            "requested_mode": payload.get("requested_mode"),
            "semantic_index_status": payload.get("semantic_index_status"),
            "source_count": payload.get("source_count"),
            "chunk_count": payload.get("chunk_count"),
            "artifact_count": len(knowledge_files),
        },
    )


def check_windows_ai_scripts(repo_root: Path) -> M16ComponentStatus:
    """Check the Windows AI/Hermes Agent helper scripts required by M16 docs."""
    scripts = (
        "00_preparar_primera_estacion.bat",
        "01_instalar_ollama.bat",
        "instalar_laia_mistral.bat",
        "construir_base_conocimiento.bat",
        "build_knowledge_base.py",
        "preparar_estacion_angel_hermes.bat",
        "comprobar_angel_hermes.bat",
        "instalar_modulo16_completo.bat",
    )
    script_dir = repo_root / "scripts" / "windows" / "ia"
    missing = [name for name in scripts if not (script_dir / name).is_file()]
    if missing:
        return M16ComponentStatus(
            name="windows_ai_scripts",
            status=STATUS_PARTIAL,
            message="Some Windows IA/Hermes Agent helper scripts are missing.",
            details={"script_dir": script_dir.as_posix(), "missing": missing},
        )
    return M16ComponentStatus(
        name="windows_ai_scripts",
        status=STATUS_READY_CONTROLLED,
        message="Required Windows IA/Hermes Agent helper scripts are present.",
        details={"script_dir": script_dir.as_posix(), "scripts": list(scripts)},
    )


def check_windows_app_launcher(repo_root: Path) -> M16ComponentStatus:
    """Check the Windows application launcher that prepares Python and starts the web app."""
    launcher = repo_root / "scripts" / "windows" / "iniciar_ojo_de_dios_windows.bat"
    if launcher.is_file():
        return M16ComponentStatus(
            name="windows_app_launcher",
            status=STATUS_READY_CONTROLLED,
            message="Windows application launcher is present.",
            details={"path": launcher.as_posix()},
        )
    return M16ComponentStatus(
        name="windows_app_launcher",
        status=STATUS_PARTIAL,
        message="Windows application launcher is missing.",
        details={"path": launcher.as_posix()},
    )


def check_laia_mistral_runtime_status(repo_root: Path) -> M16ComponentStatus:
    """Read the actual status emitted by the Windows LaIA/Mistral installer and healthcheck."""
    status_path = repo_root / "storage" / "runtime" / LAIA_MISTRAL_RUNTIME_STATUS_FILENAME
    if not status_path.is_file():
        return M16ComponentStatus(
            name="laia_mistral_runtime_status",
            status=STATUS_PARTIAL,
            message="No LaIA/Mistral runtime status has been written by the local Windows healthcheck.",
            required=False,
            details={"status_path": status_path.as_posix()},
        )
    try:
        payload = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return M16ComponentStatus(
            name="laia_mistral_runtime_status",
            status=STATUS_PARTIAL,
            message="LaIA/Mistral runtime status is unreadable.",
            required=False,
            details={"status_path": status_path.as_posix(), "error": str(error)},
        )
    if not isinstance(payload, dict):
        return M16ComponentStatus(
            name="laia_mistral_runtime_status",
            status=STATUS_PARTIAL,
            message="LaIA/Mistral runtime status has an invalid format.",
            required=False,
            details={"status_path": status_path.as_posix()},
        )
    runtime_status = str(payload.get("status", "UNKNOWN")).strip().upper()
    model = str(payload.get("model", "")).strip()
    details = {
        "status_path": status_path.as_posix(),
        "runtime_status": runtime_status,
        "model": model or None,
        "reason": payload.get("reason"),
        "checked_at": payload.get("checked_at"),
    }
    if runtime_status in {STATUS_READY_LOCAL_AI, STATUS_KNOWLEDGE_MISSING}:
        if model and model != MISTRAL_OFFICIAL_MODEL:
            return M16ComponentStatus(
                name="laia_mistral_runtime_status",
                status=STATUS_MODEL_MISSING,
                message="Windows healthcheck reported a local model different from the configured official Mistral model.",
                required=False,
                details=details,
            )
        return M16ComponentStatus(
            name="laia_mistral_runtime_status",
            status=STATUS_READY_LOCAL_AI,
            message="Windows LaIA/Mistral healthcheck reported a usable local model runtime.",
            required=False,
            details=details,
        )
    if runtime_status == STATUS_MODEL_MISSING:
        return M16ComponentStatus(
            name="laia_mistral_runtime_status",
            status=STATUS_MODEL_MISSING,
            message="Windows LaIA/Mistral healthcheck reported that the configured model is missing.",
            required=False,
            details=details,
        )
    if runtime_status == STATUS_MISSING_TOOL:
        return M16ComponentStatus(
            name="laia_mistral_runtime_status",
            status=STATUS_MISSING_TOOL,
            message="Windows LaIA/Mistral healthcheck reported that a required local tool is missing.",
            required=False,
            details=details,
        )
    return M16ComponentStatus(
        name="laia_mistral_runtime_status",
        status=STATUS_PARTIAL if runtime_status != STATUS_FAILED else STATUS_FAILED,
        message="Windows LaIA/Mistral healthcheck has not reported a ready local model runtime.",
        required=False,
        details=details,
    )


def check_hermes_lab_workspace(repo_root: Path) -> M16ComponentStatus:
    """Check the Hermes laboratory workspace documentation and root directory."""
    lab_dir = repo_root / "modules" / "laboratory"
    readme = lab_dir / "README_ANGEL_HERMES.md"
    if lab_dir.is_dir() and readme.is_file():
        return M16ComponentStatus(
            name="hermes_lab_workspace",
            status=STATUS_LAB_WORKSPACE_READY,
            message="Hermes laboratory workspace exists and is documented.",
            details={"path": lab_dir.as_posix(), "readme": readme.as_posix()},
        )
    return M16ComponentStatus(
        name="hermes_lab_workspace",
        status=STATUS_PARTIAL,
        message="Hermes laboratory workspace or documentation is missing.",
        details={"path": lab_dir.as_posix(), "readme": readme.as_posix()},
    )


def check_ai_environment(env: Mapping[str, str] | None = None) -> M16ComponentStatus:
    """Check AI-related environment flags without exposing secrets or calling networks."""
    env = os.environ if env is None else env
    ai_enabled = _env_enabled(env, "AI_ENABLED")
    mistral_enabled = _env_enabled(env, "MISTRAL_ENABLED") if ai_enabled else False
    angel_enabled = _env_enabled(env, "ANGEL_ENABLED") if ai_enabled else False
    model = env.get("MISTRAL_MODEL", MISTRAL_OFFICIAL_MODEL)
    details = _safe_env_flag_details(
        env,
        ("AI_ENABLED", "MISTRAL_ENABLED", "ANGEL_ENABLED", "MISTRAL_MODEL", "DEEPSEEK_API_KEY"),
    )
    details.update(
        {
            "ai_enabled": ai_enabled,
            "mistral_evaluated": ai_enabled,
            "angel_evaluated": ai_enabled,
            "mistral_enabled": mistral_enabled,
            "angel_enabled": angel_enabled,
        }
    )
    if not ai_enabled:
        return M16ComponentStatus(
            name="ai_environment",
            status=STATUS_DISABLED,
            message="AI_ENABLED is not active; Mistral and Hermes Agent runtime flags are not evaluated.",
            required=False,
            details=details,
        )
    if mistral_enabled and model != MISTRAL_OFFICIAL_MODEL:
        return M16ComponentStatus(
            name="ai_environment",
            status=STATUS_MODEL_MISSING,
            message="MISTRAL_MODEL does not match the official local model required by M16.",
            details=details,
        )
    return M16ComponentStatus(
        name="ai_environment",
        status=STATUS_READY_CONTROLLED,
        message="AI environment flags are internally consistent.",
        required=False,
        details=details,
    )


def check_python_tool_health() -> M16ComponentStatus:
    """Check the Python runtime through ToolHealth and VersionLock metadata."""
    resolved_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    lock = create_locked_entry(
        tool_id="python.runtime",
        tool_name="Python runtime",
        module_id=M16_MODULE_ID,
        recommended_version=resolved_version,
        resolved_version=resolved_version,
        runtime=RUNTIME_PYTHON,
    )
    result = check_tool_health(
        ToolHealthSpec(
            tool_id="python.runtime",
            executable=sys.executable,
            version_args=("--version",),
        ),
        lock,
    )
    return M16ComponentStatus(
        name="toolhealth_python_runtime",
        status=result.status,
        message=result.message,
        details=result.to_dict(),
    )


def check_local_ai_tools(env: Mapping[str, str] | None = None) -> M16ComponentStatus:
    """Check local AI tool availability only when AI/Mistral is enabled."""
    env = os.environ if env is None else env
    if not _env_enabled(env, "AI_ENABLED") or not _env_enabled(env, "MISTRAL_ENABLED"):
        return M16ComponentStatus(
            name="local_ai_tools",
            status=STATUS_DISABLED,
            message="Local AI tool availability not required because AI/Mistral is disabled.",
            required=False,
        )
    ollama_path = shutil.which("ollama")
    if ollama_path is None:
        return M16ComponentStatus(
            name="local_ai_tools",
            status=STATUS_MISSING_TOOL,
            message="Ollama executable is missing from PATH.",
            details={"tool": "ollama"},
        )
    return M16ComponentStatus(
        name="local_ai_tools",
        status=STATUS_READY_LOCAL_AI,
        message="Ollama executable is available on PATH.",
        details={"tool": "ollama", "path": ollama_path},
    )


def _contains_secret(value: object) -> bool:
    """Return whether a JSON-compatible value appears to expose a secret."""
    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            if SECRET_KEY_PATTERN.search(str(key)):
                return True
            if _contains_secret(nested_value):
                return True
        return False
    if isinstance(value, list):
        return any(_contains_secret(item) for item in value)
    if isinstance(value, str):
        return any(pattern.search(value) for pattern in SECRET_VALUE_PATTERNS)
    return False


def check_evidence_quality(repo_root: Path) -> M16ComponentStatus:
    """Audit stored evidence payloads for basic M16 quality requirements."""
    evidence_dir = repo_root / "storage" / "evidence"
    if not evidence_dir.exists():
        return M16ComponentStatus(
            name="evidence_quality",
            status=STATUS_PARTIAL,
            message="Evidence store directory is not present yet; no stored evidence can be audited.",
            required=False,
            details={"path": evidence_dir.as_posix(), "audited_files": 0},
        )

    failures: list[dict[str, object]] = []
    audited_files = 0
    for path in sorted(evidence_dir.rglob("*.json")):
        audited_files += 1
        relative_path = path.relative_to(repo_root).as_posix()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            failures.append({"path": relative_path, "reason": "json_unreadable", "error": str(error)})
            continue
        if not isinstance(payload, dict):
            failures.append({"path": relative_path, "reason": "json_not_object"})
            continue
        missing_fields = sorted(EVIDENCE_REQUIRED_FIELDS - set(payload))
        if missing_fields:
            failures.append({"path": relative_path, "reason": "missing_required_fields", "fields": missing_fields})
        if payload.get("quality") not in VALID_EVIDENCE_QUALITIES:
            failures.append({"path": relative_path, "reason": "invalid_quality", "quality": payload.get("quality")})
        if payload.get("demo") is True and payload.get("real_execution") is True:
            failures.append({"path": relative_path, "reason": "demo_marked_real_execution"})
        if _contains_secret(payload):
            failures.append({"path": relative_path, "reason": "potential_secret_exposure"})

    if failures:
        return M16ComponentStatus(
            name="evidence_quality",
            status=STATUS_FAILED,
            message="Stored evidence quality audit found contract violations.",
            details={"path": evidence_dir.as_posix(), "audited_files": audited_files, "failures": failures[:25]},
        )
    return M16ComponentStatus(
        name="evidence_quality",
        status=STATUS_READY_CONTROLLED,
        message="Stored evidence payloads satisfy M16 basic quality checks.",
        required=False,
        details={"path": evidence_dir.as_posix(), "audited_files": audited_files},
    )


def check_version_lock_readiness() -> M16ComponentStatus:
    """Build a non-network VersionLock readiness view for M16 tools and Python."""
    resolved_python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_lock = create_locked_entry(
        tool_id="python.runtime",
        tool_name="Python runtime",
        module_id=M16_MODULE_ID,
        recommended_version=resolved_python_version,
        resolved_version=resolved_python_version,
        runtime=RUNTIME_PYTHON,
    )
    documented_tools = list_documented_tools_for_module(M16_MODULE_ID)
    review_locks = [
        create_needs_review_lock_from_tool_definition(item, M16_MODULE_ID)
        for item in documented_tools
    ]
    unresolved = [
        entry.tool_id
        for entry in review_locks
        if entry.status == VERSION_LOCK_STATUS_NEEDS_REVIEW
        and entry.recommended_version == VERSION_LOCK_RECOMMENDED_UNRESOLVED
    ]
    status = STATUS_READY_CONTROLLED if not unresolved else STATUS_PARTIAL
    message = (
        "M16 VersionLock readiness has locked Python and documented tool locks ready for review."
        if unresolved
        else "M16 VersionLock readiness has locked runtime metadata for all checked tools."
    )
    return M16ComponentStatus(
        name="version_lock_readiness",
        status=status,
        message=message,
        required=False,
        details={
            "locked": [
                {
                    "tool_id": python_lock.tool_id,
                    "tool_name": python_lock.tool_name,
                    "status": VERSION_LOCK_STATUS_LOCKED,
                    "resolved_version": python_lock.resolved_version,
                    "runtime": python_lock.runtime,
                }
            ],
            "needs_review": [
                {
                    "tool_id": entry.tool_id,
                    "tool_name": entry.tool_name,
                    "recommended_version": entry.recommended_version,
                    "runtime": entry.runtime,
                }
                for entry in review_locks
            ],
            "unresolved_count": len(unresolved),
        },
    )


def check_runtime_cleanup_plan(repo_root: Path) -> M16ComponentStatus:
    """Prepare a safe runtime cleanup plan without deleting runtime artifacts."""
    runtime_dir = repo_root / "storage" / "runtime"
    if not runtime_dir.exists():
        return M16ComponentStatus(
            name="runtime_cleanup_plan",
            status=STATUS_PARTIAL,
            message="Runtime directory is missing; cleanup cannot be planned yet.",
            required=False,
            details={"path": runtime_dir.as_posix(), "candidate_count": 0},
        )
    candidates: list[dict[str, object]] = []
    for path in sorted(item for item in runtime_dir.iterdir() if item.is_file()):
        if path.name == ".gitkeep":
            continue
        if path.suffix.lower() in RUNTIME_CLEANUP_SUFFIXES or path.name.lower().startswith(RUNTIME_CLEANUP_PREFIXES):
            candidates.append(
                {
                    "path": path.relative_to(repo_root).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "reason": "temporary_runtime_artifact",
                }
            )
    return M16ComponentStatus(
        name="runtime_cleanup_plan",
        status=STATUS_READY_CONTROLLED,
        message="Runtime cleanup plan prepared without deleting files.",
        required=False,
        details={
            "path": runtime_dir.as_posix(),
            "candidate_count": len(candidates),
            "candidates": candidates,
            "deletes_performed": 0,
        },
    )


def check_export_preparation(repo_root: Path) -> M16ComponentStatus:
    """Check that external export preparation files exist without integrating external products."""
    missing = [
        relative_path
        for relative_path in M16_EXPORT_REQUIRED_PATHS
        if not (repo_root / relative_path).is_file()
    ]
    if missing:
        return M16ComponentStatus(
            name="export_preparation",
            status=STATUS_PARTIAL,
            message="Some external export preparation files are missing.",
            required=False,
            details={"missing": missing, "required_paths": list(M16_EXPORT_REQUIRED_PATHS)},
        )
    return M16ComponentStatus(
        name="export_preparation",
        status=STATUS_READY_CONTROLLED,
        message="External export preparation is available without runtime integration of separate products.",
        required=False,
        details={
            "required_paths": list(M16_EXPORT_REQUIRED_PATHS),
            "external_product_integration": False,
        },
    )


def check_angel_hermes_runtime_status(repo_root: Path) -> M16ComponentStatus:
    """Read Hermes Agent runtime status when present without exposing secrets or calling APIs."""
    status_path = repo_root / "storage" / "runtime" / ANGEL_HERMES_RUNTIME_STATUS_FILENAME
    if not status_path.is_file():
        return M16ComponentStatus(
            name="angel_hermes_runtime_status",
            status=STATUS_PARTIAL,
            message="No Hermes Agent runtime status has been written by the local healthcheck.",
            required=False,
            details={"status_path": status_path.as_posix()},
        )
    try:
        payload = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return M16ComponentStatus(
            name="angel_hermes_runtime_status",
            status=STATUS_PARTIAL,
            message="Hermes Agent runtime status is unreadable.",
            required=False,
            details={"status_path": status_path.as_posix(), "error": str(error)},
        )
    if not isinstance(payload, dict):
        return M16ComponentStatus(
            name="angel_hermes_runtime_status",
            status=STATUS_PARTIAL,
            message="Hermes Agent runtime status has an invalid format.",
            required=False,
            details={"status_path": status_path.as_posix()},
        )
    if _contains_secret(payload):
        return M16ComponentStatus(
            name="angel_hermes_runtime_status",
            status=STATUS_FAILED,
            message="Hermes Agent runtime status appears to expose a secret.",
            required=False,
            details={"status_path": status_path.as_posix()},
        )
    runtime_status = str(payload.get("status", "UNKNOWN")).strip().upper()
    accepted_ready = {STATUS_READY_CONTROLLED, STATUS_LAB_WORKSPACE_READY}
    return M16ComponentStatus(
        name="angel_hermes_runtime_status",
        status=STATUS_READY_CONTROLLED if runtime_status in accepted_ready else STATUS_PARTIAL,
        message="Hermes Agent runtime status was read from local healthcheck output.",
        required=False,
        details={
            "status_path": status_path.as_posix(),
            "runtime_status": runtime_status,
            "provider": payload.get("provider"),
            "model": payload.get("model"),
            "checked_at": payload.get("checked_at"),
        },
    )


def derive_overall_status(components: tuple[M16ComponentStatus, ...]) -> str:
    """Derive an honest overall M16 status from component states."""
    if any(component.required and component.status == STATUS_FAILED for component in components):
        return STATUS_FAILED
    if any(component.required and component.status in {STATUS_MISSING_TOOL, STATUS_MODEL_MISSING} for component in components):
        return STATUS_PARTIAL
    if any(component.status in {STATUS_PARTIAL, STATUS_KNOWLEDGE_MISSING, STATUS_KNOWLEDGE_STALE, STATUS_DISABLED} for component in components):
        return STATUS_PARTIAL
    if all(component.status in {STATUS_READY_CONTROLLED, STATUS_READY_LOCAL_AI, STATUS_LAB_WORKSPACE_READY} for component in components):
        return STATUS_READY_CONTROLLED
    return STATUS_PARTIAL



@dataclass(frozen=True, slots=True)
class M16OperationalActionResult:
    """JSON-safe result emitted by a guided M16 control-center action."""

    action: str
    status: str
    message: str
    mutation_performed: bool
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "action": self.action,
            "status": self.status,
            "message": self.message,
            "mutation_performed": self.mutation_performed,
            "details": self.details,
        }


def _relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _write_json_atomic(target_path: Path, payload: Mapping[str, object]) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(target_path)
    return target_path


def _runtime_dir_for_repo(repo_root: Path) -> Path:
    return repo_root / "storage" / "runtime"


def _resolve_output_path(root: Path, output_path: Path | None, default_name: str) -> Path:
    runtime_dir = _runtime_dir_for_repo(root).resolve()
    target = (runtime_dir / default_name) if output_path is None else output_path
    resolved = target.resolve() if target.is_absolute() else (root / target).resolve()
    try:
        resolved.relative_to(runtime_dir)
    except ValueError as error:
        raise ValueError("M16 action output_path must stay inside storage/runtime.") from error
    if resolved.suffix.lower() != ".json":
        raise ValueError("M16 action output_path must be a JSON file.")
    return resolved


def _validate_runtime_cleanup_root(repo_root: Path, runtime_dir: Path) -> Path:
    root = repo_root.resolve()
    resolved = runtime_dir.resolve()
    expected = (root / "storage" / "runtime").resolve()
    if resolved != expected:
        raise ValueError("M16 cleanup is restricted to the repository storage/runtime directory.")
    if resolved in {root, root.parent, Path(resolved.anchor).resolve()}:
        raise ValueError("Refusing unsafe runtime cleanup path.")
    return resolved


def clean_m16_runtime(repo_root: Path | None = None) -> M16OperationalActionResult:
    """Delete only planned temporary M16 runtime artifacts under storage/runtime."""
    root = Path.cwd() if repo_root is None else repo_root
    runtime_dir = _runtime_dir_for_repo(root)
    try:
        safe_runtime_dir = _validate_runtime_cleanup_root(root, runtime_dir)
    except ValueError as error:
        return M16OperationalActionResult(
            action="clean_runtime",
            status=STATUS_FAILED,
            message=str(error),
            mutation_performed=False,
            details={"runtime_dir": runtime_dir.as_posix()},
        )
    if not safe_runtime_dir.exists():
        return M16OperationalActionResult(
            action="clean_runtime",
            status=STATUS_PARTIAL,
            message="Runtime directory does not exist; nothing was deleted.",
            mutation_performed=False,
            details={"runtime_dir": runtime_dir.as_posix(), "deleted_count": 0},
        )

    plan = check_runtime_cleanup_plan(root)
    deleted: list[str] = []
    errors: list[dict[str, str]] = []
    for candidate in plan.details.get("candidates", []):
        relative = str(candidate.get("path", "")) if isinstance(candidate, Mapping) else ""
        path = (root / relative).resolve()
        try:
            path.relative_to(safe_runtime_dir)
        except ValueError:
            errors.append({"path": relative, "error": "candidate_outside_runtime"})
            continue
        if not path.is_file():
            continue
        try:
            path.unlink()
            deleted.append(_relative_or_absolute(path, root))
        except OSError as error:
            errors.append({"path": relative, "error": str(error)})

    status = STATUS_READY_CONTROLLED if not errors else STATUS_PARTIAL
    return M16OperationalActionResult(
        action="clean_runtime",
        status=status,
        message=f"Runtime cleanup completed; deleted {len(deleted)} temporary artifact(s).",
        mutation_performed=bool(deleted),
        details={
            "runtime_dir": _relative_or_absolute(runtime_dir, root),
            "planned_count": int(plan.details.get("candidate_count", 0)),
            "deleted_count": len(deleted),
            "deleted": deleted,
            "errors": errors,
        },
    )


def force_m16_recheck(repo_root: Path | None = None, env: Mapping[str, str] | None = None) -> M16OperationalActionResult:
    """Recompute readiness now without persisting or mutating runtime state."""
    report = build_m16_readiness_report(repo_root=repo_root, env=env)
    return M16OperationalActionResult(
        action="force_recheck",
        status=report.status,
        message="M16 readiness was recomputed from local checks without side effects.",
        mutation_performed=False,
        details={"readiness": report.to_dict(), "component_count": len(report.components)},
    )


def export_m16_readiness_report(
    output_path: Path | None = None,
    repo_root: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> M16OperationalActionResult:
    """Export the current M16 readiness report to a JSON artifact."""
    root = Path.cwd() if repo_root is None else repo_root
    report = build_m16_readiness_report(repo_root=root, env=env)
    try:
        target_path = _resolve_output_path(root, output_path, "m16_readiness_export.json")
    except ValueError as error:
        return M16OperationalActionResult(
            action="export_readiness",
            status=STATUS_FAILED,
            message=str(error),
            mutation_performed=False,
        )
    payload = {
        "schema_version": "m16.readiness_export.v1",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "readiness": report.to_dict(),
    }
    _write_json_atomic(target_path, payload)
    return M16OperationalActionResult(
        action="export_readiness",
        status=STATUS_READY_CONTROLLED,
        message=f"Readiness export written to {_relative_or_absolute(target_path, root)}.",
        mutation_performed=True,
        details={
            "artifact_path": _relative_or_absolute(target_path, root),
            "readiness_status": report.status,
        },
    )


def write_m16_version_lock_snapshot(output_path: Path | None = None, repo_root: Path | None = None) -> M16OperationalActionResult:
    """Write a local VersionLock snapshot for M16 without external version resolution."""
    root = Path.cwd() if repo_root is None else repo_root
    status = check_version_lock_readiness()
    try:
        target_path = _resolve_output_path(root, output_path, "m16_version_lock_snapshot.json")
    except ValueError as error:
        return M16OperationalActionResult(
            action="version_lock",
            status=STATUS_FAILED,
            message=str(error),
            mutation_performed=False,
        )
    payload = {
        "schema_version": "m16.version_lock_snapshot.v1",
        "module_id": M16_MODULE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "external_resolution_performed": False,
        "version_lock_readiness": status.to_dict(),
    }
    _write_json_atomic(target_path, payload)
    return M16OperationalActionResult(
        action="version_lock",
        status=status.status,
        message=f"VersionLock snapshot written to {_relative_or_absolute(target_path, root)} without network resolution.",
        mutation_performed=True,
        details={
            "artifact_path": _relative_or_absolute(target_path, root),
            "external_resolution_performed": False,
            **status.details,
        },
    )


def run_m16_operational_action(
    action: str,
    parameters: Mapping[str, object] | None = None,
    repo_root: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> M16OperationalActionResult:
    """Dispatch a guided M16 action by stable action id."""
    parameters = {} if parameters is None else parameters
    normalized = action.strip().lower().replace("-", "_")
    output = parameters.get("output_path")
    output_path = Path(str(output)) if output else None
    if normalized == "clean_runtime":
        return clean_m16_runtime(repo_root=repo_root)
    if normalized == "force_recheck":
        return force_m16_recheck(repo_root=repo_root, env=env)
    if normalized == "export_readiness":
        return export_m16_readiness_report(output_path=output_path, repo_root=repo_root, env=env)
    if normalized == "version_lock":
        return write_m16_version_lock_snapshot(output_path=output_path, repo_root=repo_root)
    return M16OperationalActionResult(
        action=normalized or action,
        status=STATUS_FAILED,
        message="Unknown M16 operational action.",
        mutation_performed=False,
        details={"supported_actions": ["clean_runtime", "force_recheck", "export_readiness", "version_lock"]},
    )

def build_m16_readiness_report(
    repo_root: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> M16ReadinessReport:
    """Build a local M16 readiness report without side effects."""
    root = Path.cwd() if repo_root is None else repo_root
    components = (
        check_module_manifest_integrity(),
        check_runtime_storage(root),
        check_workspace_root(root),
        check_ai_prompts(root),
        check_knowledge_base(root),
        check_windows_ai_scripts(root),
        check_windows_app_launcher(root),
        check_laia_mistral_runtime_status(root),
        check_hermes_lab_workspace(root),
        check_angel_hermes_runtime_status(root),
        check_evidence_quality(root),
        check_version_lock_readiness(),
        check_runtime_cleanup_plan(root),
        check_export_preparation(root),
        check_ai_environment(env),
        check_python_tool_health(),
        check_local_ai_tools(env),
    )
    return M16ReadinessReport(
        module_id=M16_MODULE_ID,
        status=derive_overall_status(components),
        generated_at=datetime.now(timezone.utc).isoformat(),
        components=components,
    )


def write_runtime_status(
    report: M16ReadinessReport,
    runtime_dir: Path | None = None,
) -> Path:
    """Persist an M16 readiness report as JSON without exposing secret values."""
    target_dir = Path("storage/runtime") if runtime_dir is None else runtime_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / RUNTIME_STATUS_FILENAME
    target_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    append_m16_readiness_history(report, target_dir)
    return target_path
