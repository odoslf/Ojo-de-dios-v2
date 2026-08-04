"""Documentation-backed module technique catalog contract tests."""

from app.core.technique_catalog import list_module_techniques, summarize_module_techniques


def test_technique_catalog_extracts_heading_techniques_with_metadata() -> None:
    techniques = list_module_techniques("m07_post_exploitation")
    havoc = next(item for item in techniques if item.technique_id == "post.c2.havoc_deploy")

    assert havoc.catalog_module_id == "m07_post_exploitation"
    assert havoc.module_id == "post_exploitation"
    assert havoc.doc_path == "docs/techniques/07_POST_EXPLOITATION.md"
    assert havoc.metadata["tool"] == "Havoc"
    assert havoc.metadata["worker"] == "C2Worker"
    assert havoc.to_dict()["execution_implied"] is False


def test_technique_catalog_extracts_bullet_techniques_and_summary() -> None:
    techniques = list_module_techniques("m14_phishing")
    summary = summarize_module_techniques()

    assert any(item.technique_id == "phishing.credential_harvesting" for item in techniques)
    assert summary["module_counts"]["m14_phishing"] == len(techniques)
    assert summary["total_techniques"] >= len(techniques)
    assert summary["execution_implied"] is False
