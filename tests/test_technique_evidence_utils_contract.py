from app.core.technique_evidence_utils import stable_evidence_id, utc_now_iso


def test_stable_evidence_id_is_deterministic_and_namespaced() -> None:
    first = stable_evidence_id("run-1", "technique.x", "summary")
    second = stable_evidence_id("run-1", "technique.x", "summary")
    different = stable_evidence_id("run-1", "technique.x", "details")

    assert first == second
    assert first.startswith("ev-")
    assert first != different


def test_utc_now_iso_returns_aware_utc_timestamp() -> None:
    value = utc_now_iso()

    assert value.endswith("+00:00")
    assert "T" in value
