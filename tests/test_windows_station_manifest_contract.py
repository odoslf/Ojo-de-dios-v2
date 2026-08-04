"""Windows station manifest contract tests."""

from fastapi.testclient import TestClient

from app.core.windows_station_manifest import build_windows_station_manifest
from app.main import create_app


def test_windows_station_manifest_is_ready_and_uses_official_sources() -> None:
    manifest = build_windows_station_manifest()

    assert manifest["ready"] is True
    assert manifest["model"]["official_mistral_model"] == "CognitiveComputations/dolphin-mistral-nemo:12b"
    assert manifest["model"]["ollama_windows_download_url"] == "https://ollama.com/download/windows"
    assert manifest["hermes_agent"]["repository_url"] == "https://github.com/NousResearch/hermes-agent"
    assert manifest["hermes_agent"]["writes_production_directly"] is False
    assert manifest["working_rules"]["no_fake_success"] is True
    assert manifest["github_zip_supported"] is True
    assert manifest["local_exporter_required"] is False
    assert all(item["exists"] for item in manifest["files"])


def test_windows_station_manifest_api_and_m16_page_expose_handoff() -> None:
    client = TestClient(create_app())

    api_response = client.get("/api/ops/m16/windows-station-manifest")
    page_response = client.get("/ops/m16")

    assert api_response.status_code == 200
    payload = api_response.json()["station_manifest"]
    assert payload["local_entrypoints"]["start_app"] == "scripts\\windows\\iniciar_ojo_de_dios_windows.bat"
    assert payload["local_entrypoints"]["github_zip_first_run"] == "scripts\\windows\\iniciar_ojo_de_dios_windows.bat"
    assert payload["local_entrypoints"]["local_copy_export_zip_optional"] == "scripts\\windows\\exportar_ojo_de_dios_zip.bat"
    assert page_response.status_code == 200
    assert "Manifiesto de estación Windows" in page_response.text
    assert "https://ollama.com/download/windows" in page_response.text
