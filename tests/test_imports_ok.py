"""Import smoke tests for the base application chassis."""


def test_base_imports_ok() -> None:
    import app
    from app.config import get_settings
    from app.core.product_identity import get_product_display_name
    from app.main import create_app

    assert app is not None
    assert create_app is not None
    assert get_settings is not None
    assert get_product_display_name is not None
