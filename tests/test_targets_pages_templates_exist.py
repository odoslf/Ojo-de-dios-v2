"""Template existence tests for target pages."""

from pathlib import Path


def test_target_page_templates_and_css_exist() -> None:
    expected_paths = [
        Path("app/templates/base.html"),
        Path("app/templates/targets/new.html"),
        Path("app/templates/targets/detail.html"),
        Path("app/templates/modules/index.html"),
        Path("app/static/css/app.css"),
    ]
    for path in expected_paths:
        assert path.exists()


def test_new_target_template_contains_required_content() -> None:
    content = Path("app/templates/targets/new.html").read_text()
    assert "Nuevo objetivo" in content
    assert "/api/targets/create" in content
    assert "target_type" in content
    assert "dry_run" in content


def test_detail_template_contains_disabled_actions() -> None:
    content = Path("app/templates/targets/detail.html").read_text()
    assert "Planificar" in content
    assert "no disponible todavía" in content


def test_modules_template_contains_catalog_and_readiness_content() -> None:
    content = Path("app/templates/modules/index.html").read_text()
    assert "Módulos de Ojo de Dios" in content
    assert "Readiness M16" in content
    assert "/api/ops/m16/readiness" in content
    assert "module.workspace_path" in content
