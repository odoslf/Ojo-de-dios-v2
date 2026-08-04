"""M16 Windows installer contract tests."""

from pathlib import Path


def test_m16_full_installer_exists_and_delegates_to_real_scripts() -> None:
    script = Path("scripts/windows/ia/instalar_modulo16_completo.bat")
    content = script.read_text(encoding="utf-8")

    assert script.is_file()
    assert "00_preparar_primera_estacion.bat" in content
    assert "01_instalar_ollama.bat" in content
    assert "03_probar_mistral.bat" in content
    assert "construir_base_conocimiento.bat" in content
    assert "preparar_estacion_angel_hermes.bat" in content
    assert "comprobar_angel_hermes.bat" in content
    assert "m16_full_install_status.json" in content
    assert "scripts\\windows\\iniciar_ojo_de_dios_windows.bat" in content
    assert "CognitiveComputations/dolphin-mistral-nemo:12b" in content
    assert "stub" not in content.lower()


def test_m16_readiness_tracks_full_windows_installer() -> None:
    status = Path("app/modules/m16_ops_quality/status.py").read_text(encoding="utf-8")

    assert "instalar_modulo16_completo.bat" in status


def test_windows_app_launcher_prepares_real_app_start() -> None:
    script = Path("scripts/windows/iniciar_ojo_de_dios_windows.bat")
    content = script.read_text(encoding="utf-8")

    assert script.is_file()
    assert "requirements.txt" in content
    assert "uvicorn app.main:app" in content
    assert "windows_app_start_status.json" in content
    assert "app.core.windows_first_run" in content
    assert "http://%HOST%:%PORT%/modules" in content
    assert 'start "" "http://%HOST%:%PORT%/modules"' in content
