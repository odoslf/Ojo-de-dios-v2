"""Windows/GitHub ZIP first-run contract tests."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.windows_first_run import build_first_run_report, write_first_run_status
from app.main import create_app


def test_first_run_report_checks_local_requirements_without_external_calls(tmp_path: Path) -> None:
    report = build_first_run_report()
    payload = report.to_dict()

    assert payload["external_api_call_performed"] is False
    assert payload["model_download_performed"] is False
    assert {check["name"] for check in payload["checks"]} >= {
        "python_3_12",
        "required_project_files",
        "env_file",
        "runtime_writable",
        "python_dependencies",
        "port_8000_available",
    }
    status_path = write_first_run_status(report, repo_root=tmp_path)
    assert status_path.name == "windows_first_run_status.json"
    assert status_path.is_file()


def test_first_run_api_and_page_persist_status() -> None:
    runtime_path = Path("storage/runtime/windows_first_run_status.json")
    if runtime_path.exists():
        runtime_path.unlink()
    with TestClient(create_app()) as client:
        api_response = client.get("/api/ops/m16/first-run")
        write_response = client.post("/api/ops/m16/first-run/write")
        page_response = client.get("/ops/m16/first-run")
        page_write_response = client.post("/ops/m16/first-run/write")

    assert api_response.status_code == 200
    assert write_response.status_code == 200
    assert write_response.json()["status_path"] == "storage/runtime/windows_first_run_status.json"
    assert page_response.status_code == 200
    assert "Comprobación de primer arranque" in page_response.text
    assert page_write_response.status_code == 200
    assert "FIRST_RUN_WRITTEN" in page_write_response.text
    assert runtime_path.is_file()
    runtime_path.unlink()
