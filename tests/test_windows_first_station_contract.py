from pathlib import Path


FIRST_STATION = Path("scripts/windows/ia/00_preparar_primera_estacion.bat")
INSTALLER = Path("scripts/windows/ia/instalar_laia_mistral.bat")
M16_STATUS = Path("app/modules/m16_ops_quality/status.py")


def test_first_station_preflight_is_present_and_non_installing() -> None:
    script = FIRST_STATION.read_text(encoding="utf-8")

    assert "READY_FOR_WINDOWS_INSTALLATION" in script
    assert "downloads_performed\":false" in script
    assert "external_api_calls_performed\":false" in script
    assert "CognitiveComputations/dolphin-mistral-nemo:12b" in script
    assert "DEEPSEEK_MODEL=deepseek-v4-pro" in script
    assert "DEEPSEEK_FAST_MODEL=deepseek-v4-flash" in script
    assert "DEEPSEEK_API_KEY=ALAZAN_REEMPLAZAR_EN_ENV_LOCAL" in script
    assert "ollama pull" not in script.lower()
    assert "/chat/completions" not in script.lower()
    assert "api/models" not in script.lower()


def test_main_installer_exposes_first_station_preflight_before_download() -> None:
    installer = INSTALLER.read_text(encoding="utf-8")

    assert "0. Preparar primera estacion sin descargar ni llamar APIs" in installer
    assert 'if "%OPCION%"=="0" goto preparar_primera_estacion' in installer
    assert 'call "%SCRIPT_DIR%00_preparar_primera_estacion.bat"' in installer
    assert installer.index("0. Preparar primera estacion") < installer.index("1. Instalar/comprobar Ollama")


def test_m16_readiness_tracks_first_station_script() -> None:
    status_source = M16_STATUS.read_text(encoding="utf-8")

    assert '"00_preparar_primera_estacion.bat"' in status_source
    assert status_source.index('"00_preparar_primera_estacion.bat"') < status_source.index('"01_instalar_ollama.bat"')
