"""M03 network-service mapping from persisted M02 observations.

The mapper consumes already recorded evidence. It does not scan, connect to, or
otherwise interact with a target. Any runnable technique references are taken
only from the runtime registry, never invented from service names.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.m02_vulnerability_inventory import read_m02_service_inventory
from app.core.runtime_registry import RuntimeRegistrySnapshot, get_runtime_registry_snapshot
from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M03_MODULE_ID = "m03_network_services"


def _service_family(product: str, port: object) -> str:
    """Classify an observed service for operator triage without assigning exploitability."""
    name = product.casefold()
    number = int(port) if isinstance(port, int) else None
    if number in {80, 443, 8080, 8443} or any(token in name for token in ("http", "nginx", "apache", "iis")):
        return "web"
    if number in {22, 23, 3389, 5900} or any(token in name for token in ("ssh", "telnet", "rdp", "vnc")):
        return "remote_access"
    if number in {25, 110, 143, 465, 587, 993, 995} or any(token in name for token in ("smtp", "imap", "pop")):
        return "mail"
    if number in {53, 5353} or "dns" in name:
        return "name_resolution"
    if number in {1433, 1521, 3306, 5432, 6379, 27017} or any(token in name for token in ("mysql", "postgres", "mssql", "oracle", "redis", "mongo")):
        return "database"
    return "other"


def _registered_m03_techniques(snapshot: RuntimeRegistrySnapshot) -> list[dict[str, object]]:
    """Return only concrete M03 techniques that are actually present in the runtime registry."""
    return [metadata for metadata in snapshot.registry.to_metadata_list() if metadata["module_id"] == M03_MODULE_ID]


def build_m03_service_map(
    target: TargetRecord,
    repo_root: Path | None = None,
    registry_snapshot: RuntimeRegistrySnapshot | None = None,
) -> dict[str, object]:
    """Build an evidence-only M03 map from the latest M02 inventory."""
    inventory = read_m02_service_inventory(target, repo_root=repo_root)
    snapshot = get_runtime_registry_snapshot() if registry_snapshot is None else registry_snapshot
    techniques = _registered_m03_techniques(snapshot)
    services = inventory.get("services", []) if isinstance(inventory, dict) else []
    mapped_services: list[dict[str, object]] = []
    for item in services if isinstance(services, list) else []:
        if not isinstance(item, dict):
            continue
        product = str(item.get("product", "")).strip()
        if not product:
            continue
        mapped_services.append({
            "product": product,
            "version": item.get("version"),
            "transport": item.get("transport"),
            "port": item.get("port"),
            "service_family": _service_family(product, item.get("port")),
            "evidence_ref": item.get("evidence_ref"),
            "nvd_candidate_count": len(item.get("nvd_candidates", [])) if isinstance(item.get("nvd_candidates"), list) else 0,
            "operator_next_step": "Validate ownership, scope and configuration before selecting any technique.",
            "target_activity_performed": False,
        })
    return {
        "schema_version": 1,
        "target_id": target.target_id,
        "module_id": M03_MODULE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_inventory_found": inventory is not None,
        "source_inventory_path": f"storage/targets/{target.target_id}/modules/m02_vulnerabilities/evidence/service_inventory.json",
        "services": mapped_services,
        "service_count": len(mapped_services),
        "registered_m03_techniques": techniques,
        "registered_m03_technique_count": len(techniques),
        "target_activity_performed": False,
        "execution_started": False,
    }


def write_m03_service_map(target: TargetRecord, repo_root: Path | None = None) -> Path:
    """Persist the current evidence-only M03 map in the target M03 workspace."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M03_MODULE_ID, repo_root=root)
    path = binding.root_path / "outputs" / "service_map.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_m03_service_map(target, repo_root=root), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_m03_service_map(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object] | None:
    """Read a persisted M03 map without modifying workspaces or contacting the target."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M03_MODULE_ID, repo_root=root)
    path = binding.root_path / "outputs" / "service_map.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None
