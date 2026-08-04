"""Technique registry loading helpers."""

import importlib
import inspect
import pkgutil
from types import ModuleType

from app.contracts.technique_contract import BaseTechnique
from app.core.technique_registry import TechniqueRegistry, create_empty_registry


def is_technique_class(obj: object) -> bool:
    """Return whether an object is a concrete BaseTechnique subclass."""
    return inspect.isclass(obj) and issubclass(obj, BaseTechnique) and obj is not BaseTechnique


def iter_technique_classes_from_module(module: object) -> list[type[BaseTechnique]]:
    """Return technique classes declared on a module without instantiating them."""
    technique_classes: list[type[BaseTechnique]] = []
    for _, obj in inspect.getmembers(module):
        if is_technique_class(obj):
            technique_classes.append(obj)
    return sorted(technique_classes, key=lambda technique_cls: technique_cls.__name__)


def import_module_by_name(module_name: str) -> object:
    """Import and return a module by exact name."""
    return importlib.import_module(module_name)


def load_registry_from_classes(technique_classes: list[type[BaseTechnique]]) -> TechniqueRegistry:
    """Create a registry from explicit technique classes."""
    registry = create_empty_registry()
    registry.register_many(technique_classes)
    return registry


def load_registry_from_module_names(module_names: list[str]) -> TechniqueRegistry:
    """Create a registry from exact module names."""
    technique_classes: list[type[BaseTechnique]] = []
    for module_name in module_names:
        module = import_module_by_name(module_name)
        technique_classes.extend(iter_technique_classes_from_module(module))
    return load_registry_from_classes(technique_classes)


def discover_technique_classes(
    package_name: str,
    recursive: bool = True,
    allow_missing: bool = False,
) -> list[type[BaseTechnique]]:
    """Discover technique classes from a package or module."""
    try:
        package = importlib.import_module(package_name)
    except ModuleNotFoundError:
        if allow_missing:
            return []
        raise

    technique_classes = iter_technique_classes_from_module(package)
    package_path = getattr(package, "__path__", None)
    if not recursive or package_path is None:
        return technique_classes

    prefix = f"{package.__name__}."
    for module_info in pkgutil.walk_packages(package_path, prefix):
        module = importlib.import_module(module_info.name)
        if isinstance(module, ModuleType):
            technique_classes.extend(iter_technique_classes_from_module(module))
    return technique_classes


def load_registry_from_package(
    package_name: str,
    recursive: bool = True,
    allow_missing: bool = False,
) -> TechniqueRegistry:
    """Create a registry from discovered package technique classes."""
    technique_classes = discover_technique_classes(package_name, recursive, allow_missing)
    return load_registry_from_classes(technique_classes)
