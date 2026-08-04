"""Create a Windows-ready Ojo de Dios ZIP without secrets or runtime artifacts."""

from __future__ import annotations

import argparse
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

EXCLUDED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", "dist"}
EXCLUDED_STORAGE_CHILDREN = {"runtime", "logs", "tmp", "targets", "evidence", "job_logs", "reports", "models"}
EXCLUDED_FILENAMES = {".env", "ojo_de_dios.sqlite3"}
REQUIRED_HANDOFF_FILES = (
    "app/main.py",
    "requirements.txt",
    ".env.example",
    "scripts/windows/iniciar_ojo_de_dios_windows.bat",
    "scripts/windows/ia/instalar_modulo16_completo.bat",
)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def should_include(path: Path, repo_root: Path) -> bool:
    relative = path.relative_to(repo_root)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if relative.name in EXCLUDED_FILENAMES:
        return False
    if len(relative.parts) >= 2 and relative.parts[0] == "storage" and relative.parts[1] in EXCLUDED_STORAGE_CHILDREN:
        return False
    return path.is_file()


def validate_required_files(repo_root: Path) -> list[str]:
    return [relative for relative in REQUIRED_HANDOFF_FILES if not (repo_root / relative).is_file()]


def build_export_manifest(repo_root: Path, zip_path: Path, included_files: list[str]) -> dict[str, object]:
    return {
        "manifest_type": "ojo_de_dios_zip_export",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "zip_path": zip_path.as_posix(),
        "included_file_count": len(included_files),
        "excluded_secret_files": sorted(EXCLUDED_FILENAMES),
        "excluded_runtime_storage": sorted(EXCLUDED_STORAGE_CHILDREN),
        "windows_start": "scripts\\windows\\iniciar_ojo_de_dios_windows.bat",
        "m16_install": "scripts\\windows\\ia\\instalar_modulo16_completo.bat",
        "contains_env_file": ".env" in included_files,
        "contains_git_directory": any(item.startswith(".git/") for item in included_files),
    }


def export_project_zip(repo_root: Path, output_dir: Path | None = None) -> tuple[Path, dict[str, object]]:
    root = repo_root.resolve()
    missing = validate_required_files(root)
    if missing:
        raise FileNotFoundError(f"Missing required handoff files: {', '.join(missing)}")
    target_dir = (root / "dist") if output_dir is None else output_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    zip_path = target_dir / f"Ojo-de-Dios-windows-ready-{utc_stamp()}.zip"
    included_files: list[str] = []
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if not should_include(path, root):
                continue
            relative = path.relative_to(root).as_posix()
            included_files.append(relative)
            archive.write(path, arcname=f"Ojo-de-Dios/{relative}")
    manifest = build_export_manifest(root, zip_path, included_files)
    manifest_path = target_dir / "latest_zip_export_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return zip_path, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Ojo de Dios as a Windows-ready ZIP.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults to ./dist.")
    args = parser.parse_args()
    zip_path, manifest = export_project_zip(
        repo_root=Path(args.repo_root),
        output_dir=Path(args.output_dir) if args.output_dir else None,
    )
    print(json.dumps({"zip_path": zip_path.as_posix(), "manifest": manifest}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
