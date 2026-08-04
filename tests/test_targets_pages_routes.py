"""Route tests for target HTML pages."""

from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.web.routes_targets_pages as target_pages
from app.db.session import init_db
from app.main import create_app


def _override_page_session(monkeypatch) -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    init_db(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def override_get_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    monkeypatch.setattr(target_pages, "get_session", override_get_session)


def test_new_target_page_renders() -> None:
    client = TestClient(create_app())
    response = client.get("/targets/new")
    assert response.status_code == 200
    assert "Nuevo objetivo" in response.text
    assert "Ojo de Dios" in response.text
    assert "/api/targets/create" in response.text


def test_missing_target_detail_returns_404(monkeypatch) -> None:
    _override_page_session(monkeypatch)
    client = TestClient(create_app())
    response = client.get("/targets/no-existe")
    assert response.status_code == 404
