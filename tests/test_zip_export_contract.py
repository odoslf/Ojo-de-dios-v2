"""ZIP export contract tests."""

from pathlib import Path
import zipfile

from scripts.export_project_zip import export_project_zip


def test_export_project_zip_excludes_secrets_runtime_and_includes_windows_entrypoints(tmp_path: Path) -> None:
    zip_path, manifest = export_project_zip(repo_root=Path.cwd(), output_dir=tmp_path)

    assert zip_path.is_file()
    assert manifest["contains_env_file"] is False
    assert manifest["contains_git_directory"] is False
    assert manifest["windows_start"] == "scripts\\windows\\iniciar_ojo_de_dios_windows.bat"
    assert manifest["m16_install"] == "scripts\\windows\\ia\\instalar_modulo16_completo.bat"
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert "Ojo-de-Dios/scripts/windows/iniciar_ojo_de_dios_windows.bat" in names
    assert "Ojo-de-Dios/scripts/windows/ia/instalar_modulo16_completo.bat" in names
    assert "Ojo-de-Dios/.env" not in names
    assert not any(name.startswith("Ojo-de-Dios/storage/runtime/") for name in names)
    assert not any(name.startswith("Ojo-de-Dios/.git/") for name in names)
