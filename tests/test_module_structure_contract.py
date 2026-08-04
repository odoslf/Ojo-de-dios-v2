"""Physical module structure contract tests."""

from pathlib import Path

from app.core.module_catalog import TOTAL_MODULE_SLOTS, list_modules, require_module_by_number
from app.modules.registry import (
    MANIFEST_FILENAME,
    MODULES_ROOT,
    load_all_module_manifests,
    load_module_manifest,
    manifest_path_for,
    validate_all_module_manifests,
    workspace_path_for,
)


def test_each_catalog_module_has_a_physical_package_and_manifest() -> None:
    for module in list_modules(include_reserved=True):
        package_path = Path(module.package_path)
        manifest_path = Path(module.manifest_path)

        assert package_path.is_dir()
        assert (package_path / "__init__.py").is_file()
        assert manifest_path.is_file()
        assert manifest_path.name == MANIFEST_FILENAME


def test_physical_module_manifests_match_catalog_entries() -> None:
    validated_module_ids = validate_all_module_manifests()

    assert len(validated_module_ids) == TOTAL_MODULE_SLOTS
    assert validated_module_ids[0] == "m01_osint"
    assert validated_module_ids[-1] == "m20_future_expansion"


def test_loaded_manifests_are_in_catalog_order_and_json_ready() -> None:
    manifests = load_all_module_manifests()

    assert len(manifests) == TOTAL_MODULE_SLOTS
    assert manifests[0]["module_number"] == 1
    assert manifests[0]["workspace_path"] == "storage/workspaces/m01_osint"
    assert manifests[-1]["module_number"] == 20
    assert manifests[-1]["reserved"] is True
    assert manifests[-1]["requires_user_definition"] is True


def test_reserved_manifest_does_not_imply_doc_or_execution() -> None:
    reserved = require_module_by_number(17)
    manifest = load_module_manifest(reserved.module_id)

    assert manifest["official"] is False
    assert manifest["reserved"] is True
    assert manifest["doc_path"] is None
    assert manifest["readiness"] == "reserved_future_module"
    assert "Reserved module:" in manifest["notes"][0]


def test_registry_paths_are_resolved_inside_repo_structure() -> None:
    module = require_module_by_number(1)

    assert manifest_path_for(module).is_file()
    assert workspace_path_for(module).as_posix().endswith("storage/workspaces/m01_osint")
    assert MODULES_ROOT.as_posix().endswith("app/modules")
