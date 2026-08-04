"""Module catalog contract tests."""

from dataclasses import FrozenInstanceError

import pytest

from app.core.module_catalog import (
    MODULE_STATUS_DOCUMENTED,
    MODULE_STATUS_RESERVED_FUTURE,
    OFFICIAL_MODULE_COUNT,
    RESERVED_MODULE_COUNT,
    TOTAL_MODULE_SLOTS,
    get_module_by_id,
    get_module_by_number,
    list_modules,
    list_official_modules,
    list_reserved_modules,
    module_catalog_as_dicts,
    require_module_by_id,
    require_module_by_number,
)


def test_module_catalog_exposes_20_ordered_slots_with_16_official_modules() -> None:
    modules = list_modules()

    assert len(modules) == TOTAL_MODULE_SLOTS
    assert len(list_official_modules()) == OFFICIAL_MODULE_COUNT
    assert len(list_reserved_modules()) == RESERVED_MODULE_COUNT
    assert [module.module_number for module in modules] == list(range(1, TOTAL_MODULE_SLOTS + 1))


def test_official_modules_are_documented_and_not_reserved() -> None:
    official_modules = list_official_modules()

    assert official_modules[0].module_id == "m01_osint"
    assert official_modules[-1].module_id == "m16_ops_quality"
    assert all(module.official is True for module in official_modules)
    assert all(module.reserved is False for module in official_modules)
    assert all(module.requires_user_definition is False for module in official_modules)
    assert all(module.readiness == MODULE_STATUS_DOCUMENTED for module in official_modules)
    assert all(module.doc_path is not None for module in official_modules)


def test_reserved_modules_do_not_imply_implementation() -> None:
    reserved_modules = list_reserved_modules()

    assert [module.module_number for module in reserved_modules] == [17, 18, 19, 20]
    assert all(module.official is False for module in reserved_modules)
    assert all(module.reserved is True for module in reserved_modules)
    assert all(module.requires_user_definition is True for module in reserved_modules)
    assert all(module.readiness == MODULE_STATUS_RESERVED_FUTURE for module in reserved_modules)
    assert all(module.doc_path is None for module in reserved_modules)


def test_catalog_lookup_helpers_return_known_modules() -> None:
    assert get_module_by_number(1).module_id == "m01_osint"  # type: ignore[union-attr]
    assert get_module_by_id("m16_ops_quality").module_number == 16  # type: ignore[union-attr]
    assert require_module_by_number(20).reserved is True
    assert require_module_by_id("m17_hackrf_sdr").requires_user_definition is True


def test_catalog_lookup_helpers_reject_unknown_modules() -> None:
    assert get_module_by_number(21) is None
    assert get_module_by_id("m99_unknown") is None

    with pytest.raises(ValueError, match="Unknown module number"):
        require_module_by_number(21)
    with pytest.raises(ValueError, match="Unknown module id"):
        require_module_by_id("m99_unknown")


def test_catalog_entries_are_immutable_and_json_ready() -> None:
    module = require_module_by_number(1)
    serialized = module_catalog_as_dicts()

    assert serialized[0]["module_id"] == "m01_osint"
    assert serialized[-1]["module_id"] == "m20_future_expansion"
    assert isinstance(serialized[0]["notes"], list)
    with pytest.raises(FrozenInstanceError):
        module.display_name = "changed"  # type: ignore[misc]
