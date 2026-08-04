"""Route tests for module HTML pages."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_modules_dashboard_renders_catalog_and_m16_readiness() -> None:
    client = TestClient(create_app())

    response = client.get("/modules")

    assert response.status_code == 200
    assert "Módulos de Ojo de Dios" in response.text
    assert "Readiness M16" in response.text
    assert "m01_osint" in response.text
    assert "m20_future_expansion" in response.text
    assert "/api/ops/m16/readiness" in response.text


def test_root_route_points_to_modules_dashboard() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["next"] == "/modules"


def test_module_detail_page_renders_real_catalog_sections() -> None:
    client = TestClient(create_app())

    response = client.get("/modules/m01_osint")

    assert response.status_code == 200
    assert "OSINT" in response.text
    assert "Técnicas conectadas" in response.text
    assert "Herramientas/capacidades" in response.text
    assert "Plan de instalación" in response.text
    assert "/api/modules/m01_osint/techniques" in response.text


def test_m18_module_detail_renders_ioc_timeline_panel_and_api() -> None:
    client = TestClient(create_app())

    page_response = client.get("/modules/m18_honeypots_deception")
    api_response = client.get("/api/modules/m18_honeypots_deception/ioc-timeline")

    assert page_response.status_code == 200
    assert "Línea de tiempo IOC M18" in page_response.text
    assert "/api/modules/m18_honeypots_deception/ioc-timeline" in page_response.text
    assert api_response.status_code == 200
    assert api_response.json()["timeline"]["schema_version"] == "m18.ioc_timeline.v1"


def test_missing_module_detail_page_returns_404() -> None:
    client = TestClient(create_app())

    response = client.get("/modules/m99_unknown")

    assert response.status_code == 404


def test_module_workspace_page_renders_state_and_bootstrap_form() -> None:
    client = TestClient(create_app())

    response = client.get("/modules/m01_osint/workspace")

    assert response.status_code == 200
    assert "Workspace operativo" in response.text
    assert "Tool workspaces" in response.text
    assert "/modules/m01_osint/workspace/bootstrap" in response.text
    assert "/api/modules/m01_osint/workspace/state" in response.text


def test_missing_module_workspace_page_returns_404() -> None:
    client = TestClient(create_app())

    response = client.get("/modules/m99_unknown/workspace")

    assert response.status_code == 404


def test_m01_passive_dns_page_renders_real_form_and_posts_result() -> None:
    client = TestClient(create_app())

    get_response = client.get("/modules/m01_osint/passive-dns")
    post_response = client.post("/modules/m01_osint/passive-dns", data={"domain": "localhost"})

    assert get_response.status_code == 200
    assert "Consulta DNS pasiva" in get_response.text
    assert "/modules/m01_osint/passive-dns" in get_response.text
    assert post_response.status_code == 200
    assert "Resultado" in post_response.text
    assert "Escaneo de puertos" in post_response.text
    assert "no realizada" in post_response.text
    assert "Registros DNS" in post_response.text
    assert "Lectura operativa" in post_response.text


def test_m16_control_center_renders_safe_actions_and_can_write_readiness() -> None:
    runtime_path = Path("storage/runtime/m16_readiness_status.json")
    if runtime_path.exists():
        runtime_path.unlink()
    client = TestClient(create_app())

    get_response = client.get("/ops/m16")
    post_response = client.post("/ops/m16/readiness/write")

    assert get_response.status_code == 200
    assert "Centro de control M16" in get_response.text
    assert "scripts\\windows\\iniciar_ojo_de_dios_windows.bat" in get_response.text
    assert "Construir conocimiento local" in get_response.text
    assert "Limpiar runtime" in get_response.text
    assert "Forzar re-check" in get_response.text
    assert "Version-lock" in get_response.text
    assert "Alertas e historial readiness" in get_response.text
    assert post_response.status_code == 200
    assert "READY_WRITTEN" in post_response.text
    assert runtime_path.is_file()
    runtime_path.unlink()


def test_m16_guided_action_api_and_page_export_readiness() -> None:
    export_path = Path("storage/runtime/m16_readiness_export.json")
    if export_path.exists():
        export_path.unlink()
    client = TestClient(create_app())

    api_response = client.post("/api/ops/m16/actions/force_recheck", json={})
    page_response = client.post("/ops/m16/actions/export_readiness")

    assert api_response.status_code == 200
    assert api_response.json()["result"]["action"] == "force_recheck"
    assert api_response.json()["result"]["mutation_performed"] is False
    assert page_response.status_code == 200
    assert "Readiness export written" in page_response.text
    assert export_path.is_file()
    export_path.unlink()


def test_m16_readiness_history_api_returns_observations_after_write() -> None:
    history_path = Path("storage/runtime/m16_readiness_history.jsonl")
    alerts_path = Path("storage/runtime/m16_readiness_alerts.jsonl")
    previous_history = history_path.read_text(encoding="utf-8") if history_path.exists() else None
    previous_alerts = alerts_path.read_text(encoding="utf-8") if alerts_path.exists() else None
    client = TestClient(create_app())

    write_response = client.post("/api/ops/m16/readiness/write")
    history_response = client.get("/api/ops/m16/readiness/history?limit=1")

    assert write_response.status_code == 200
    assert history_response.status_code == 200
    payload = history_response.json()["readiness_history"]
    assert payload["history_count"] == 1
    assert payload["history"][0]["schema_version"] == "m16.readiness_history.v1"

    if previous_history is None:
        history_path.unlink(missing_ok=True)
    else:
        history_path.write_text(previous_history, encoding="utf-8")
    if previous_alerts is None:
        alerts_path.unlink(missing_ok=True)
    else:
        alerts_path.write_text(previous_alerts, encoding="utf-8")


def test_target_product_flow_page_creates_target_selects_module_and_starts_job(monkeypatch) -> None:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.db.session import init_db
    from app.web import routes_targets_pages

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    init_db(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def override_get_session():
        with session_factory() as session:
            yield session

    monkeypatch.setattr(routes_targets_pages, "get_session", override_get_session)
    client = TestClient(create_app())

    new_page = client.get("/targets/new")
    create_response = client.post(
        "/targets/new",
        data={
            "name": "Product flow",
            "target_type": "domain",
            "value": "example.com",
            "mode": "dry_run",
            "allowed_modules": "m09_scraping_intelligence",
            "noise_profile": "normal",
            "evidence_profile": "standard",
            "require_confirmations": "on",
        },
        follow_redirects=False,
    )
    target_path = create_response.headers["location"]
    detail_response = client.get(target_path)
    start_response = client.post(
        f"{target_path}/start",
        data={
            "mode": "dry_run",
            "confirmed": "on",
            "allowlisted_target": "on",
            "selected_modules": "m09_scraping_intelligence",
            "selected_techniques": "scraping.crawler.output_parser",
        },
    )

    assert new_page.status_code == 200
    assert "Módulos implementados para este objetivo" in new_page.text
    assert "m09_scraping_intelligence" in new_page.text
    assert create_response.status_code == 303
    assert detail_response.status_code == 200
    assert "Flujo producto · selección y ejecución" in detail_response.text
    assert "/start" in detail_response.text
    assert start_response.status_code == 200
    assert "Resultado del último inicio desde esta pantalla" in start_response.text
    assert "scraping.crawler.output_parser" in start_response.text
