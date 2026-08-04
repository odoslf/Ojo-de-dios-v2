"""Application runtime technique registry provider.

The provider centralizes how the product runtime builds the technique registry
from importable module packages. It does not synthesize techniques from docs and
it never creates placeholder technique classes: only real ``BaseTechnique``
subclasses present in Python packages are registered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Iterable

from app.config import get_settings
from app.core.registry_loader import discover_technique_classes, load_registry_from_classes
from app.core.technique_registry import TechniqueRegistry


@dataclass(frozen=True, slots=True)
class RegistryPackageLoadStatus:
    """Discovery status for one configured registry package."""

    package_name: str
    imported: bool
    discovered_technique_count: int
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable status payload."""
        return {
            "package_name": self.package_name,
            "imported": self.imported,
            "discovered_technique_count": self.discovered_technique_count,
            "error": self.error,
        }


@dataclass(frozen=True, slots=True)
class RuntimeRegistrySnapshot:
    """Runtime registry plus honest discovery status."""

    registry: TechniqueRegistry
    packages: tuple[RegistryPackageLoadStatus, ...] = field(default_factory=tuple)

    @property
    def technique_count(self) -> int:
        """Return the number of concrete registered techniques."""
        return self.registry.count()

    @property
    def technique_ids(self) -> tuple[str, ...]:
        """Return registered technique ids in stable order."""
        return tuple(self.registry.list_ids())

    @property
    def ready(self) -> bool:
        """Return whether every configured package imported without discovery errors."""
        return all(package.imported and package.error is None for package in self.packages)

    def to_status_payload(self) -> dict[str, object]:
        """Return a JSON-serializable runtime registry status."""
        return {
            "ready": self.ready,
            "technique_count": self.technique_count,
            "technique_ids": list(self.technique_ids),
            "packages": [package.to_dict() for package in self.packages],
            "placeholder_techniques_created": False,
            "execution_implied": False,
        }


def _normalize_package_names(package_names: str | Iterable[str]) -> tuple[str, ...]:
    if isinstance(package_names, str):
        raw_names = package_names.split(",")
    else:
        raw_names = list(package_names)
    normalized = tuple(name.strip() for name in raw_names if name and name.strip())
    return normalized or ("app.modules",)


def build_runtime_registry_snapshot(package_names: str | Iterable[str] | None = None) -> RuntimeRegistrySnapshot:
    """Discover and validate concrete technique classes from configured packages."""
    settings = get_settings()
    resolved_package_names = _normalize_package_names(
        package_names if package_names is not None else settings.technique_registry_packages
    )
    technique_classes = []
    package_statuses: list[RegistryPackageLoadStatus] = []
    for package_name in resolved_package_names:
        try:
            discovered = discover_technique_classes(package_name, recursive=True, allow_missing=False)
        except Exception as exc:  # noqa: BLE001 - status must preserve import/validation errors for health payloads.
            package_statuses.append(
                RegistryPackageLoadStatus(
                    package_name=package_name,
                    imported=False,
                    discovered_technique_count=0,
                    error=f"{exc.__class__.__name__}: {exc}",
                )
            )
            continue
        technique_classes.extend(discovered)
        package_statuses.append(
            RegistryPackageLoadStatus(
                package_name=package_name,
                imported=True,
                discovered_technique_count=len(discovered),
            )
        )
    registry = load_registry_from_classes(technique_classes)
    return RuntimeRegistrySnapshot(registry=registry, packages=tuple(package_statuses))


@lru_cache
def get_runtime_registry_snapshot() -> RuntimeRegistrySnapshot:
    """Return the cached application runtime registry snapshot."""
    return build_runtime_registry_snapshot()


def get_runtime_registry() -> TechniqueRegistry:
    """Return the cached application runtime technique registry."""
    return get_runtime_registry_snapshot().registry


def clear_runtime_registry_cache() -> None:
    """Clear the cached runtime registry snapshot after configuration changes or tests."""
    get_runtime_registry_snapshot.cache_clear()
