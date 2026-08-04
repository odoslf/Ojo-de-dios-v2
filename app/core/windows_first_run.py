"""Windows/GitHub-ZIP first-run preflight for Ojo de Dios.

The checks are local and deterministic. They do not install packages, download
models, call AI APIs, or start network scans. The Windows launcher can run this
module after dependency installation to persist a first-run status file.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import socket
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_IMPORTS = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "pydantic": "pydantic",
    "pydantic-settings": "pydantic_settings",
    "python-dotenv": "dotenv",
    "jinja2": "jinja2",
    "sqlalchemy": "sqlalchemy",
    "requests": "requests",
    "python-multipart": "python_multipart",
    "dnspython": "dns",
}
REQUIRED_PATHS = (
    "app/main.py",
    "requirements.txt",
    ".env.example",
    "scripts/windows/iniciar_ojo_de_dios_windows.bat",
    "scripts/windows/ia/instalar_modulo16_completo.bat",
)
RUNTIME_DIRS = (
    "storage",
    "storage/runtime",
    "storage/workspaces",
    "storage/knowledge",
    "modules/laboratory",
)
STATUS_FILENAME = "windows_first_run_status.json"


@dataclass(frozen=True, slots=True)
class FirstRunCheck:
    """One first-run preflight check."""

    name: str
    status: str
    message: str
    required: bool = True
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "required": self.required,
            "details": self.details,
        }


@dataclass(frozen=True, slots=True)
class FirstRunReport:
    """Complete first-run preflight report."""

    status: str
    generated_at: str
    checks: tuple[FirstRunCheck, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "generated_at": self.generated_at,
            "checks": [check.to_dict() for check in self.checks],
            "external_api_call_performed": False,
            "model_download_performed": False,
        }


def _repo_root(repo_root: Path | None = None) -> Path:
    return (Path.cwd() if repo_root is None else repo_root).resolve()


def check_python_version() -> FirstRunCheck:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info[:2] == (3, 12):
        return FirstRunCheck("python_3_12", "READY", "Python 3.12 detected.", details={"version": version})
    return FirstRunCheck("python_3_12", "FAILED", "Python 3.12 is required.", details={"version": version})


def check_required_paths(repo_root: Path | None = None) -> FirstRunCheck:
    root = _repo_root(repo_root)
    missing = [relative for relative in REQUIRED_PATHS if not (root / relative).is_file()]
    status = "READY" if not missing else "FAILED"
    return FirstRunCheck(
        "required_project_files",
        status,
        "Required GitHub ZIP project files are present." if not missing else "Some required project files are missing.",
        details={"missing": missing, "required": list(REQUIRED_PATHS)},
    )


def check_env_file(repo_root: Path | None = None) -> FirstRunCheck:
    root = _repo_root(repo_root)
    env_path = root / ".env"
    example_path = root / ".env.example"
    if env_path.is_file():
        return FirstRunCheck("env_file", "READY", ".env exists locally.", details={"path": ".env"})
    if example_path.is_file():
        return FirstRunCheck("env_file", "PARTIAL", ".env is missing but .env.example is available for the launcher to copy.", details={"path": ".env.example"}, required=False)
    return FirstRunCheck("env_file", "FAILED", "Neither .env nor .env.example exists.")


def check_runtime_writable(repo_root: Path | None = None) -> FirstRunCheck:
    root = _repo_root(repo_root)
    checked: list[str] = []
    failed: list[str] = []
    for relative in RUNTIME_DIRS:
        path = root / relative
        try:
            path.mkdir(parents=True, exist_ok=True)
            probe = path / ".write_test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            checked.append(relative)
        except OSError as exc:
            failed.append(f"{relative}: {exc}")
    return FirstRunCheck(
        "runtime_writable",
        "READY" if not failed else "FAILED",
        "Runtime directories are writable." if not failed else "Some runtime directories are not writable.",
        details={"checked": checked, "failed": failed},
    )


def check_dependencies() -> FirstRunCheck:
    missing: list[str] = []
    installed: dict[str, str] = {}
    for distribution, import_name in REQUIRED_IMPORTS.items():
        try:
            installed[distribution] = importlib.metadata.version(distribution)
            __import__(import_name)
        except (ImportError, importlib.metadata.PackageNotFoundError):
            missing.append(distribution)
    return FirstRunCheck(
        "python_dependencies",
        "READY" if not missing else "FAILED",
        "Python dependencies are importable." if not missing else "Some Python dependencies are missing.",
        details={"missing": missing, "installed": installed},
    )


def check_port_available(host: str = "127.0.0.1", port: int = 8000) -> FirstRunCheck:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        result = sock.connect_ex((host, port))
    if result == 0:
        return FirstRunCheck("port_8000_available", "PARTIAL", "Port 8000 is already in use; the app may already be running or another service is using it.", required=False, details={"host": host, "port": port})
    return FirstRunCheck("port_8000_available", "READY", "Port 8000 is available for local startup.", required=False, details={"host": host, "port": port})


def derive_status(checks: tuple[FirstRunCheck, ...]) -> str:
    if any(check.required and check.status == "FAILED" for check in checks):
        return "FAILED"
    if any(check.status in {"FAILED", "PARTIAL"} for check in checks):
        return "PARTIAL"
    return "READY"


def build_first_run_report(repo_root: Path | None = None) -> FirstRunReport:
    checks = (
        check_python_version(),
        check_required_paths(repo_root),
        check_env_file(repo_root),
        check_runtime_writable(repo_root),
        check_dependencies(),
        check_port_available(),
    )
    return FirstRunReport(
        status=derive_status(checks),
        generated_at=datetime.now(timezone.utc).isoformat(),
        checks=checks,
    )


def write_first_run_status(report: FirstRunReport, repo_root: Path | None = None) -> Path:
    root = _repo_root(repo_root)
    target_dir = root / "storage" / "runtime"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / STATUS_FILENAME
    target_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Windows first-run preflight status.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_first_run_report(Path(args.repo_root))
    payload: dict[str, object] = {"first_run": report.to_dict()}
    if args.write:
        payload["status_path"] = write_first_run_status(report, Path(args.repo_root)).as_posix()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if report.status in {"READY", "PARTIAL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
