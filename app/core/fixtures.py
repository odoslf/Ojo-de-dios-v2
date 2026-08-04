"""Local demo fixture loading utilities."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.errors import ContractError

DEFAULT_DEMO_FIXTURES_PATH = "storage/demo_fixtures"


@dataclass
class DemoFixture:
    """Loaded demo fixture payload."""

    fixture_name: str
    path: str
    payload: dict[str, Any]


class DemoFixtureStore:
    """Load local JSON demo fixtures from a configured directory."""

    def __init__(self, base_path: str | Path = DEFAULT_DEMO_FIXTURES_PATH) -> None:
        self.base_path = Path(base_path).resolve()

    def get_fixture_path(self, fixture_name: str) -> Path:
        """Return the resolved path for a safe fixture name."""
        normalized_name = self._normalize_fixture_name(fixture_name)
        fixture_path = (self.base_path / normalized_name).resolve()
        if fixture_path.parent != self.base_path:
            raise ContractError("Fixture path must stay within the demo fixtures directory.")
        return fixture_path

    def exists(self, fixture_name: str) -> bool:
        """Return whether a local fixture exists."""
        return self.get_fixture_path(fixture_name).is_file()

    def load(self, fixture_name: str) -> DemoFixture:
        """Load a local UTF-8 JSON fixture and require a JSON object payload."""
        fixture_path = self.get_fixture_path(fixture_name)
        if not fixture_path.is_file():
            raise FileNotFoundError(str(fixture_path))
        with fixture_path.open("r", encoding="utf-8") as fixture_file:
            payload = json.load(fixture_file)
        if not isinstance(payload, dict):
            raise ContractError("Demo fixture payload must be a JSON object.")
        return DemoFixture(
            fixture_name=fixture_path.name,
            path=str(fixture_path),
            payload=payload,
        )

    def list_fixture_names(self) -> list[str]:
        """Return sorted local JSON fixture names."""
        if not self.base_path.exists():
            return []
        return sorted(path.name for path in self.base_path.glob("*.json") if path.is_file())

    def _normalize_fixture_name(self, fixture_name: str) -> str:
        if not fixture_name:
            raise ContractError("Fixture name cannot be empty.")
        if ".." in fixture_name:
            raise ContractError("Fixture name cannot contain parent traversal.")
        if "/" in fixture_name or "\\" in fixture_name:
            raise ContractError("Fixture name cannot contain path separators.")
        if not fixture_name.endswith(".json"):
            return f"{fixture_name}.json"
        return fixture_name
