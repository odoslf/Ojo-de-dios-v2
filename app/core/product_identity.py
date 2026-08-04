"""Product identity helpers for Ojo de Dios."""

from os import getenv

from app.core.constants import (
    APP_VERSION_DEFAULT,
    PRODUCT_DISPLAY_NAME_DEFAULT,
    PRODUCT_INTERNAL_NAME_DEFAULT,
)


def get_product_internal_name() -> str:
    """Return the configured internal product name."""
    return getenv("PRODUCT_INTERNAL_NAME", PRODUCT_INTERNAL_NAME_DEFAULT)


def get_product_display_name() -> str:
    """Return the configured display product name."""
    return getenv("PRODUCT_DISPLAY_NAME", PRODUCT_DISPLAY_NAME_DEFAULT)


def get_product_version() -> str:
    """Return the configured product version."""
    return getenv("APP_VERSION", APP_VERSION_DEFAULT)
