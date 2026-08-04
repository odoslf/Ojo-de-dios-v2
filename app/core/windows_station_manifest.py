"""Windows station manifest for the M16 operator handoff.

The manifest is deterministic and repository-local. It does not download tools or
call external services; it tells the Windows station exactly which real entry
points, official sources, local rules, and working areas are available.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

OFFICIAL_MISTRAL_MODEL = "CognitiveComputations/dolphin-mistral-nemo:12b"
OLLAMA_WINDOWS_DOWNLOAD_URL = "https://ollama.com/download/windows"
HERMES_AGENT_REPOSITORY_URL = "https://github.com/NousResearch/hermes-agent"
HERMES_AGENT_DOCUMENTATION_URL = "https://hermes-agent.nousresearch.com/docs/"
DEEPSEEK_API_URL = "https://api.deepseek.com"


@dataclass(frozen=True, slots=True)
class StationFileStatus:
    """Presence of one required handoff file."""

    path: str
    exists: bool
    purpose: str

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "exists": self.exists, "purpose": self.purpose}


REQUIRED_FILES: tuple[tuple[str, str], ...] = (
    ("scripts/windows/iniciar_ojo_de_dios_windows.bat", "arrancar la aplicación web local desde el ZIP descargado de GitHub"),
    ("scripts/windows/ia/instalar_modulo16_completo.bat", "instalar/verificar LaIA Mistral, conocimiento y Hermes Agent"),
    ("scripts/windows/ia/01_instalar_ollama.bat", "instalar o comprobar Ollama y descargar el modelo oficial"),
    ("scripts/windows/ia/03_probar_mistral.bat", "probar el modelo local con Ollama"),
    ("scripts/windows/ia/construir_base_conocimiento.bat", "construir base de conocimiento local docs-only o semántica"),
    ("scripts/windows/ia/preparar_estacion_angel_hermes.bat", "preparar workspace Hermes Agent"),
    ("scripts/windows/ia/comprobar_angel_hermes.bat", "comprobar Hermes Agent con DeepSeek desde .env local"),
    (".env.example", "plantilla segura de configuración local"),
    ("docs/ai_prompts/laia_mistral_system_prompt.md", "reglas de sistema LaIA/Mistral"),
    ("docs/ai_prompts/angel_hermes_system_prompt.md", "reglas de sistema Hermes Agent"),
    ("docs/MODULE_EXTENSION_PLAYBOOK.md", "cómo añadir módulos/capacidades sin romper el catálogo"),
    ("docs/HERMES_TOOL_ADOPTION_PIPELINE.md", "cómo Hermes prepara herramientas en laboratorio"),
)

OPTIONAL_FILES: tuple[tuple[str, str], ...] = (
    ("scripts/windows/exportar_ojo_de_dios_zip.bat", "crear ZIP limpio si el operador trabaja desde una copia local, no obligatorio para ZIP de GitHub"),
    ("scripts/export_project_zip.py", "exportador reproducible sin secretos ni runtime para copias locales"),
)


def build_windows_station_manifest(repo_root: Path | None = None) -> dict[str, object]:
    """Return the complete Windows handoff manifest for the current repository."""
    root = Path.cwd() if repo_root is None else repo_root
    files = tuple(
        StationFileStatus(path=relative_path, exists=(root / relative_path).is_file(), purpose=purpose)
        for relative_path, purpose in REQUIRED_FILES
    )
    optional_files = tuple(
        StationFileStatus(path=relative_path, exists=(root / relative_path).is_file(), purpose=purpose)
        for relative_path, purpose in OPTIONAL_FILES
    )
    return {
        "manifest_type": "m16_windows_station_handoff",
        "ready": all(item.exists for item in files),
        "model": {
            "official_mistral_model": OFFICIAL_MISTRAL_MODEL,
            "local_backend": "ollama",
            "ollama_windows_download_url": OLLAMA_WINDOWS_DOWNLOAD_URL,
            "model_pull_command": f"ollama pull {OFFICIAL_MISTRAL_MODEL}",
        },
        "hermes_agent": {
            "repository_url": HERMES_AGENT_REPOSITORY_URL,
            "documentation_url": HERMES_AGENT_DOCUMENTATION_URL,
            "provider": "deepseek",
            "api_url": DEEPSEEK_API_URL,
            "workspace": "modules/laboratory",
            "writes_production_directly": False,
            "requires_operator_approval": True,
        },
        "local_entrypoints": {
            "github_zip_first_run": "scripts\\windows\\iniciar_ojo_de_dios_windows.bat",
            "start_app": "scripts\\windows\\iniciar_ojo_de_dios_windows.bat",
            "install_m16_ai": "scripts\\windows\\ia\\instalar_modulo16_completo.bat",
            "m16_control_center": "http://127.0.0.1:8000/ops/m16",
            "m01_passive_dns": "http://127.0.0.1:8000/modules/m01_osint/passive-dns",
            "local_copy_export_zip_optional": "scripts\\windows\\exportar_ojo_de_dios_zip.bat",
        },
        "working_rules": {
            "no_fake_success": True,
            "no_secret_commit": True,
            "mistral_receives_system_prompt_each_request": True,
            "hermes_sandbox_only_until_approved": True,
            "knowledge_base_before_big_ai_tasks": True,
        },
        "operator_flow": [
            "descargar ZIP desde GitHub y extraerlo en Windows",
            "ejecutar scripts\\windows\\iniciar_ojo_de_dios_windows.bat dentro de la carpeta extraída",
            "abrir Centro M16 y construir conocimiento local",
            "ejecutar scripts\\windows\\ia\\instalar_modulo16_completo.bat para Ollama/Mistral/Hermes",
            "usar M01 DNS pasivo para primera comprobación segura",
            "crear propuestas Hermes solo en modules/laboratory y promocionarlas con aprobación",
        ],
        "files": [item.to_dict() for item in files],
        "optional_files": [item.to_dict() for item in optional_files],
        "github_zip_supported": True,
        "local_exporter_required": False,
    }
