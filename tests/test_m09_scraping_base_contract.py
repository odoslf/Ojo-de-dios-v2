import json
import sqlite3

from app.contracts.evidence_contract import RESULT_SUCCESS
from app.contracts.technique_contract import STATUS_READY_CONTROLLED, TechniqueExecutionContext
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.registry_loader import load_registry_from_package
from app.modules.m09_scraping_intelligence.techniques import (
    CrawlerOutputParserTechnique,
    CsvExportTechnique,
    HtmlExtractionParserTechnique,
    JsonExportTechnique,
    JsonRowsNormalizerTechnique,
    PersistentWorkQueueEnqueueTechnique,
    PublicSourceConnectorTechnique,
    RobotsRateLimitPolicyTechnique,
    RssAtomParserTechnique,
    SqliteTableWriterTechnique,
)


def _context(parameters: dict[str, object]) -> TechniqueExecutionContext:
    return TechniqueExecutionContext(target_id="target-1", run_id="run-1", mode="controlled", parameters=parameters, confirmed=True)


def test_m09_registers_base_non_ai_scraping_infrastructure() -> None:
    registry = load_registry_from_package("app.modules.m09_scraping_intelligence")

    base_ids = [technique_id for technique_id in registry.list_ids() if not technique_id.startswith("scraping.ai.")]
    assert base_ids == [
        "scraping.advanced.rss_atom",
        "scraping.connectors.public_sources",
        "scraping.crawler.output_parser",
        "scraping.export.csv",
        "scraping.export.json",
        "scraping.parser.html_extraction",
        "scraping.parser.json_rows_normalizer",
        "scraping.policy.robots_rate_limit",
        "scraping.queue.persistent_enqueue",
        "scraping.storage.sqlite_table_writer",
    ]
    for technique_cls in [registry.require(technique_id) for technique_id in base_ids]:
        technique = technique_cls()
        technique.validate_metadata()
        assert technique.module_id == "m09_scraping_intelligence"
        assert technique.permission_level == PERMISSION_PASSIVE
        assert technique.implementation_status == STATUS_READY_CONTROLLED
        assert technique.requires_user_implementation is False
        assert technique.requires_network is (technique.technique_id == "scraping.connectors.public_sources")
        assert "ai" not in technique.technique_id


def test_crawler_output_parser_normalizes_text_and_jsonl_urls() -> None:
    raw = 'https://example.com/a\n{"url":"/relative"}\nnoise https://example.com/a#fragment'

    result = CrawlerOutputParserTechnique().execute(_context({"crawler_output": raw, "base_url": "https://example.com/root/"}))
    content = result.evidence[0].content

    assert result.result_status == RESULT_SUCCESS
    assert content["discovered_urls"] == ["https://example.com/a", "https://example.com/relative"]
    assert content["crawl_summary"]["url_count"] == 2


def test_html_extraction_parser_extracts_links_and_title() -> None:
    html = '<html><head><title> Example page </title></head><body><a href="/next">next</a><img src="https://cdn.example/img.png"></body></html>'

    result = HtmlExtractionParserTechnique().execute(_context({"html_content": html, "base_url": "https://example.com/start"}))
    content = result.evidence[0].content

    assert content["discovered_urls"] == ["https://example.com/next", "https://cdn.example/img.png"]
    assert content["extracted_rows"] == [{"field": "title", "value": "Example page"}]


def test_json_rows_normalizer_supports_nested_record_path() -> None:
    payload = json.dumps({"data": {"items": [{"name": "alpha", "score": 1}, {"name": "beta", "score": 2}]}})

    result = JsonRowsNormalizerTechnique().execute(_context({"json_content": payload, "record_path": "data.items"}))
    content = result.evidence[0].content

    assert content["row_count"] == 2
    assert content["extracted_rows"][1] == {"name": "beta", "score": 2}


def test_rss_atom_parser_normalizes_feed_items() -> None:
    feed = """<rss><channel><item><title>Alpha</title><link>https://example.com/a</link><pubDate>Wed, 22 Jul 2026 00:00:00 GMT</pubDate></item></channel></rss>"""

    result = RssAtomParserTechnique().execute(_context({"rss_atom_content": feed}))
    content = result.evidence[0].content

    assert content["source_summary"]["item_count"] == 1
    assert content["extracted_rows"] == [{"title": "Alpha", "url": "https://example.com/a", "published": "Wed, 22 Jul 2026 00:00:00 GMT"}]


def test_sqlite_table_writer_persists_rows_with_safe_schema(tmp_path) -> None:
    sqlite_path = tmp_path / "scraping.sqlite3"

    result = SqliteTableWriterTechnique().execute(
        _context({"sqlite_path": sqlite_path.as_posix(), "table_name": "items", "rows": [{"name": "alpha", "price": 1.25}, {"name": "beta", "price": 2.5}]})
    )

    assert result.result_status == RESULT_SUCCESS
    with sqlite3.connect(sqlite_path) as connection:
        rows = connection.execute('SELECT name, price FROM "items" ORDER BY name').fetchall()
    assert rows == [("alpha", 1.25), ("beta", 2.5)]
    assert result.evidence[0].content["inserted_rows"] == 2


def test_csv_and_json_export_write_real_files(tmp_path) -> None:
    rows = [{"name": "alpha", "score": 1}, {"name": "beta", "score": 2}]
    csv_path = tmp_path / "out.csv"
    json_path = tmp_path / "out.json"

    csv_result = CsvExportTechnique().execute(_context({"rows": rows, "output_path": csv_path.as_posix()}))
    json_result = JsonExportTechnique().execute(_context({"rows": rows, "output_path": json_path.as_posix()}))

    assert csv_result.evidence[0].content["export_reference"]["path"] == csv_path.as_posix()
    assert csv_path.read_text(encoding="utf-8").splitlines() == ["name,score", "alpha,1", "beta,2"]
    assert json.loads(json_path.read_text(encoding="utf-8")) == rows
    assert json_result.evidence[0].content["row_count"] == 2


def test_persistent_work_queue_enqueue_survives_reopen_and_deduplicates(tmp_path) -> None:
    queue_path = tmp_path / "queue.sqlite3"

    first = PersistentWorkQueueEnqueueTechnique().execute(_context({"queue_path": queue_path.as_posix(), "urls": ["https://example.com/a", "https://example.com/a#frag", "https://example.com/b"], "priority": 10}))
    second = PersistentWorkQueueEnqueueTechnique().execute(_context({"queue_path": queue_path.as_posix(), "urls": ["https://example.com/a", "https://example.com/c"], "priority": 20}))

    with sqlite3.connect(queue_path) as connection:
        rows = connection.execute("SELECT url, domain, status, priority FROM work_items ORDER BY url").fetchall()

    assert first.evidence[0].content["inserted_count"] == 2
    assert second.evidence[0].content["inserted_count"] == 1
    assert second.evidence[0].content["duplicate_count"] == 1
    assert rows == [
        ("https://example.com/a", "example.com", "pending", 10),
        ("https://example.com/b", "example.com", "pending", 10),
        ("https://example.com/c", "example.com", "pending", 20),
    ]


def test_robots_rate_limit_policy_blocks_disallowed_paths_and_persists_delay(tmp_path) -> None:
    queue_path = tmp_path / "queue.sqlite3"
    robots_txt = "User-agent: *\nDisallow: /private\n"
    urls = ["https://example.com/public", "https://example.com/private/secret"]

    first = RobotsRateLimitPolicyTechnique().execute(_context({"queue_path": queue_path.as_posix(), "urls": urls, "robots_txt": robots_txt, "delay_seconds": 30, "now_epoch": 100.0}))
    second = RobotsRateLimitPolicyTechnique().execute(_context({"queue_path": queue_path.as_posix(), "urls": ["https://example.com/other"], "robots_txt": robots_txt, "delay_seconds": 30, "now_epoch": 110.0}))

    assert first.evidence[0].content["allowed_urls"] == ["https://example.com/public"]
    assert first.evidence[0].content["blocked_urls"] == ["https://example.com/private/secret"]
    assert second.evidence[0].content["policy_decisions"][0]["allowed_by_rate_limit"] is False
    assert second.evidence[0].content["policy_decisions"][0]["wait_seconds"] == 20.0


def test_public_source_connector_fetches_configured_sources_and_deduplicates(monkeypatch) -> None:
    class FakeResponse:
        def __init__(self, text: str, content_type: str = "application/json", status_code: int = 200) -> None:
            self.text = text
            self.headers = {"content-type": content_type}
            self.status_code = status_code

    responses = {
        "https://feed.example/json": FakeResponse('{"items":[{"title":"Alpha","url":"https://example.com/a"},{"title":"Alpha","url":"https://example.com/a#fragment"}]}'),
        "https://feed.example/rss": FakeResponse('<rss><channel><item><title>Beta</title><link>https://example.com/b</link></item></channel></rss>', "application/rss+xml"),
    }

    def fake_get(url, headers=None, timeout=20):
        assert headers["user-agent"] == "ojo-test"
        return responses[url]

    monkeypatch.setattr("app.modules.m09_scraping_intelligence.techniques.requests.get", fake_get)

    result = PublicSourceConnectorTechnique().execute(
        _context(
            {
                "user_agent": "ojo-test",
                "sources": [
                    {"name": "json-source", "url": "https://feed.example/json", "type": "json"},
                    {"name": "rss-source", "url": "https://feed.example/rss", "type": "rss"},
                ],
            }
        )
    )
    content = result.evidence[0].content

    assert content["record_count"] == 2
    assert content["duplicate_count"] == 1
    assert [item["source_name"] for item in content["source_results"]] == ["json-source", "rss-source"]
    assert {item["url"] for item in content["deduplicated_records"]} == {"https://example.com/a", "https://example.com/b"}
