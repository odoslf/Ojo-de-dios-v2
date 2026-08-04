"""Attack-surface graph contract tests."""

from app.core.attack_surface_graph import build_attack_surface_graph
from app.core.target_fingerprint import build_target_fingerprint
from app.core.target_model import TARGET_EMAIL, TARGET_URL, TargetRecord


def _target(target_type: str, value: str, normalized_value: str, allowed_modules: list[str] | None = None) -> TargetRecord:
    return TargetRecord(
        target_id="target-graph-1",
        name="Graph Target",
        target_type=target_type,
        value=value,
        normalized_value=normalized_value,
        mode="dry_run",
        allowed_modules=allowed_modules or [],
    )


def test_url_target_graph_derives_url_host_protocol_and_module_nodes() -> None:
    target = _target(TARGET_URL, "https://Example.COM/login", "https://example.com/login", ["m01_osint"])
    fingerprint = build_target_fingerprint(target.target_id, target.target_type, target.value)

    graph = build_attack_surface_graph(target, fingerprint)
    payload = graph.to_dict()
    node_types = {node["node_type"] for node in payload["nodes"]}
    relationships = {edge["relationship"] for edge in payload["edges"]}

    assert payload["target_id"] == "target-graph-1"
    assert payload["source"] == "target_fingerprint"
    assert payload["checksum"]
    assert {"target", "url", "domain", "protocol", "module"}.issubset(node_types)
    assert {"HAS_ATTACK_SURFACE", "URL_HOSTS_ON", "USES_PROTOCOL", "ALLOWS_MODULE"}.issubset(relationships)
    assert payload["node_count"] == len(payload["nodes"])
    assert payload["edge_count"] == len(payload["edges"])


def test_email_target_graph_derives_domain_without_external_lookup() -> None:
    target = _target(TARGET_EMAIL, "User@Example.COM", "user@example.com")
    fingerprint = build_target_fingerprint(target.target_id, target.target_type, target.value)

    graph = build_attack_surface_graph(target, fingerprint)
    nodes = {node["node_id"]: node for node in graph.to_dict()["nodes"]}
    edges = {(edge["source_id"], edge["relationship"], edge["target_id"]) for edge in graph.to_dict()["edges"]}

    assert "email:user@example.com" in nodes
    assert "domain:example.com" in nodes
    assert ("email:user@example.com", "EMAIL_USES_DOMAIN", "domain:example.com") in edges


def test_graph_checksum_is_stable_for_same_input() -> None:
    target = _target(TARGET_URL, "https://example.com/a", "https://example.com/a")
    fingerprint = build_target_fingerprint(target.target_id, target.target_type, target.value)

    first = build_attack_surface_graph(target, fingerprint)
    second = build_attack_surface_graph(target, fingerprint)

    assert first.checksum == second.checksum
