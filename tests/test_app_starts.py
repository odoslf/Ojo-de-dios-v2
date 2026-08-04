"""Application startup tests."""

from fastapi import FastAPI

from app.main import create_app


def test_create_app_returns_fastapi_instance() -> None:
    fastapi_app = create_app()

    assert isinstance(fastapi_app, FastAPI)


def test_app_title_uses_default_product_display_name() -> None:
    fastapi_app = create_app()

    assert fastapi_app.title == "Ojo de Dios"
