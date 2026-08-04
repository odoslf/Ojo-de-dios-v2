"""Technique registry extensibility tests."""

from app.core.registry_loader import load_registry_from_module_names, load_registry_from_package

PLUGIN_SOURCE = '''
from app.contracts.technique_contract import BaseTechnique, STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
from app.core.permission_levels import PERMISSION_PASSIVE

class SamplePluginTechnique(BaseTechnique):
    technique_id = "plugin.sample"
    module_id = "plugin"
    display_name = "Sample Plugin"
    description = "Sample plugin technique"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "none"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True
'''

PLUGIN_A_SOURCE = PLUGIN_SOURCE.replace("SamplePluginTechnique", "PluginATechnique").replace(
    "plugin.sample", "plugin.a"
).replace("Sample Plugin", "Plugin A")

PLUGIN_B_SOURCE = PLUGIN_SOURCE.replace("SamplePluginTechnique", "PluginBTechnique").replace(
    "plugin.sample", "plugin.b"
).replace("Sample Plugin", "Plugin B")


def test_registry_loads_dynamic_module_without_central_changes(tmp_path, monkeypatch) -> None:
    (tmp_path / "sample_plugin.py").write_text(PLUGIN_SOURCE, encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))

    registry = load_registry_from_module_names(["sample_plugin"])

    assert registry.count() == 1
    assert registry.get("plugin.sample") is not None
    assert registry.to_metadata_list()[0]["module_id"] == "plugin"


def test_registry_loads_dynamic_package_without_central_changes(tmp_path, monkeypatch) -> None:
    package_dir = tmp_path / "sample_package"
    package_dir.mkdir()
    (package_dir / "init.py").write_text("# package marker\n", encoding="utf-8")
    (package_dir / "plugin_a.py").write_text(PLUGIN_A_SOURCE, encoding="utf-8")
    (package_dir / "plugin_b.py").write_text(PLUGIN_B_SOURCE, encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))

    registry = load_registry_from_package("sample_package", recursive=True)

    assert registry.count() == 2
    assert registry.get("plugin.a") is not None
    assert registry.get("plugin.b") is not None
