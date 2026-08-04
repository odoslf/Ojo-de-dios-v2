"""Concrete base infrastructure for M09 scraping intelligence.

Ronda 12 intentionally implements only local/read-only scraping infrastructure:
normalizers, parsers, SQLite persistence, and CSV/JSON export helpers.  The AI
planning/analysis techniques documented for M09 stay outside this file until the
AI integration round.  No technique bypasses access controls, solves CAPTCHAs,
rotates proxies, or scrapes targets without operator-supplied data.
"""

from __future__ import annotations

import csv
import json
import re
import sqlite3
import hashlib
import requests
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from app.contracts.evidence_contract import EVIDENCE_QUALITY_HIGH, EvidenceRecord, RESULT_SUCCESS
from app.contracts.technique_contract import BaseTechnique, STATUS_READY_CONTROLLED, TechniqueExecutionContext, TechniqueExecutionResult
from app.core.errors import ContractError
from app.core.technique_evidence_utils import stable_evidence_id, utc_now_iso
from app.core.permission_levels import PERMISSION_PASSIVE

M09_MODULE_ID = "m09_scraping_intelligence"
_SAFE_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,62}$")
_URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
_DEFAULT_SQLITE_PATH = Path("storage/workspaces/m09_scraping_intelligence/scraping_results.sqlite3")
_ALLOWED_SCALAR_TYPES = (str, int, float, bool, type(None))


def _evidence(context: TechniqueExecutionContext, technique_id: str, suffix: str, summary: str, content: dict[str, Any]) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=stable_evidence_id(context.run_id, technique_id, suffix),
        run_id=context.run_id,
        target_id=context.target_id,
        technique_id=technique_id,
        module_id=M09_MODULE_ID,
        evidence_type=suffix,
        quality=EVIDENCE_QUALITY_HIGH,
        summary=summary,
        content=content,
        source="m09-scraping-base",
        demo=False,
        real_execution=True,
        created_at=utc_now_iso(),
    )


def _string_parameter(parameters: dict[str, Any], name: str, *, required: bool = True) -> str:
    value = parameters.get(name)
    if value is None:
        if required:
            raise ContractError(f"{name} is required.")
        return ""
    text = str(value).strip()
    if required and not text:
        raise ContractError(f"{name} cannot be empty.")
    return text


def _list_of_dicts(parameters: dict[str, Any], name: str) -> list[dict[str, Any]]:
    value = parameters.get(name)
    if not isinstance(value, list):
        raise ContractError(f"{name} must be a list of objects.")
    rows: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ContractError(f"{name} entries must be objects.")
        rows.append(dict(item))
    return rows


def _safe_identifier(identifier: str, *, label: str = "identifier") -> str:
    value = identifier.strip()
    if not _SAFE_IDENTIFIER_PATTERN.fullmatch(value):
        raise ContractError(f"{label} must be a safe SQLite identifier.")
    return value


def _workspace_output_path(path_text: str | None, default_path: Path) -> Path:
    path = Path(path_text).expanduser() if path_text else default_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _normalize_url(url: str, base_url: str = "") -> str | None:
    candidate = urljoin(base_url, url.strip()) if base_url else url.strip()
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return parsed._replace(fragment="").geturl()


def _unique_urls(urls: list[str], base_url: str = "") -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for url in urls:
        value = _normalize_url(str(url), base_url)
        if value and value not in seen:
            seen.add(value)
            normalized.append(value)
    return normalized


class _LinkParser(HTMLParser):
    def __init__(self, base_url: str = "") -> None:
        super().__init__()
        self.base_url = base_url
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name.lower() in {"href", "src", "action"} and value:
                normalized = _normalize_url(value, self.base_url)
                if normalized:
                    self.urls.append(normalized)


def _extract_urls_from_html(html: str, base_url: str = "") -> list[str]:
    parser = _LinkParser(base_url)
    parser.feed(html)
    return _unique_urls(parser.urls + _URL_PATTERN.findall(html), base_url)


def _extract_urls_from_text(raw: str, base_url: str = "") -> list[str]:
    urls: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            urls.extend(_URL_PATTERN.findall(stripped))
            if stripped.startswith(("/", "http://", "https://")):
                urls.append(stripped)
            continue
        if isinstance(parsed, dict):
            for key in ("url", "endpoint", "href", "request_url"):
                if parsed.get(key):
                    urls.append(str(parsed[key]))
        elif isinstance(parsed, str):
            urls.append(parsed)
    return _unique_urls(urls, base_url)


def _read_text_parameter(parameters: dict[str, Any], content_name: str, path_name: str) -> tuple[str, str | None]:
    if parameters.get(content_name) is not None:
        return str(parameters[content_name]), None
    path_text = _string_parameter(parameters, path_name)
    path = Path(path_text)
    if not path.is_file():
        raise ContractError(f"{path_name} does not point to a readable file.")
    return path.read_text(encoding="utf-8"), path.as_posix()


def _infer_columns(rows: list[dict[str, Any]]) -> list[str]:
    columns: list[str] = []
    for row in rows:
        for key in row:
            safe = _safe_identifier(str(key), label="row key")
            if safe not in columns:
                columns.append(safe)
    if not columns:
        raise ContractError("At least one row column is required.")
    return columns


def _sqlite_type(value: Any) -> str:
    if isinstance(value, bool) or isinstance(value, int):
        return "INTEGER"
    if isinstance(value, float):
        return "REAL"
    return "TEXT"


def _adapt_value(value: Any) -> Any:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, _ALLOWED_SCALAR_TYPES):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _create_table_and_insert(sqlite_path: Path, table_name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ContractError("rows must include at least one object.")
    safe_table = _safe_identifier(table_name, label="table_name")
    columns = _infer_columns(rows)
    sample_by_column = {column: next((row.get(column) for row in rows if row.get(column) is not None), "") for column in columns}
    column_defs = ", ".join(f'"{column}" {_sqlite_type(sample_by_column[column])}' for column in columns)
    placeholders = ", ".join("?" for _ in columns)
    quoted_columns = ", ".join(f'"{column}"' for column in columns)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(sqlite_path) as connection:
        connection.execute(f'CREATE TABLE IF NOT EXISTS "{safe_table}" ({column_defs})')
        connection.executemany(
            f'INSERT INTO "{safe_table}" ({quoted_columns}) VALUES ({placeholders})',
            [[_adapt_value(row.get(column)) for column in columns] for row in rows],
        )
        total_rows = connection.execute(f'SELECT COUNT(*) FROM "{safe_table}"').fetchone()[0]
    return {"sqlite_path": sqlite_path.as_posix(), "table_name": safe_table, "columns": columns, "inserted_rows": len(rows), "total_rows": int(total_rows)}


def _parse_rss_atom(raw: str) -> list[dict[str, Any]]:
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as error:
        raise ContractError("rss_atom_content must be valid XML.") from error
    items: list[dict[str, Any]] = []
    for element in list(root.findall(".//item")) + list(root.findall(".//{http://www.w3.org/2005/Atom}entry")):
        def text_for(names: tuple[str, ...]) -> str:
            for name in names:
                found = element.find(name)
                if found is not None and found.text:
                    return found.text.strip()
            return ""

        link = text_for(("link", "{http://www.w3.org/2005/Atom}link"))
        atom_link = element.find("{http://www.w3.org/2005/Atom}link")
        if atom_link is not None and atom_link.get("href"):
            link = atom_link.get("href", "").strip()
        items.append(
            {
                "title": text_for(("title", "{http://www.w3.org/2005/Atom}title")),
                "url": link,
                "published": text_for(("pubDate", "published", "updated", "{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated")),
            }
        )
    return items


class CrawlerOutputParserTechnique(BaseTechnique):
    """Normalize operator-supplied crawler output into unique URL evidence."""

    technique_id = "scraping.crawler.output_parser"
    module_id = M09_MODULE_ID
    display_name = "Crawler output parser"
    description = "Parse existing crawler stdout, JSONL, or text artifacts into normalized discovered URLs."
    tool_name = "internal_crawler_parser"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "ScrapingWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["crawler_output", "crawler_output_path", "base_url"]
    expected_evidence = ["discovered_urls", "crawl_summary", "normalized_json"]
    input_schema = {"crawler_output": {"type": "string"}, "crawler_output_path": {"type": "string"}, "base_url": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "crawler_output", "label": "Crawler output", "type": "textarea"}]
    success_markers = ["discovered_urls"]
    failure_markers = ["missing_crawler_output"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"discovered_urls": "list", "crawl_summary": "dict"}
    version_lock_id = "m09_scraping_intelligence/crawler-output-parser"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        raw, source_path = _read_text_parameter(context.parameters, "crawler_output", "crawler_output_path")
        urls = _extract_urls_from_text(raw, _string_parameter(context.parameters, "base_url", required=False))
        content = {"discovered_urls": urls, "crawl_summary": {"url_count": len(urls), "source_path": source_path}, "raw_output_path": source_path}
        evidence = _evidence(context, self.technique_id, "discovered_urls", "Crawler output parsed into normalized URLs.", content)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class HtmlExtractionParserTechnique(BaseTechnique):
    """Extract links and lightweight rows from supplied HTML content."""

    technique_id = "scraping.parser.html_extraction"
    module_id = M09_MODULE_ID
    display_name = "HTML extraction parser"
    description = "Parse operator-supplied HTML into discovered links and simple text rows without browser automation."
    tool_name = "html.parser"
    recommended_version = "python-stdlib"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["html_content", "html_path", "base_url"]
    expected_evidence = ["discovered_urls", "extracted_rows", "normalized_json"]
    input_schema = {"html_content": {"type": "string"}, "html_path": {"type": "string"}, "base_url": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "html_content", "label": "HTML content", "type": "textarea"}]
    success_markers = ["discovered_urls", "extracted_rows"]
    failure_markers = ["missing_html_content"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"discovered_urls": "list", "extracted_rows": "list"}
    version_lock_id = "m09_scraping_intelligence/html-extraction-parser"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        html, source_path = _read_text_parameter(context.parameters, "html_content", "html_path")
        urls = _extract_urls_from_html(html, _string_parameter(context.parameters, "base_url", required=False))
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        rows = [{"field": "title", "value": re.sub(r"\s+", " ", title_match.group(1)).strip()}] if title_match else []
        content = {"discovered_urls": urls, "extracted_rows": rows, "source_path": source_path, "url_count": len(urls)}
        evidence = _evidence(context, self.technique_id, "html_extraction", "HTML content parsed into links and lightweight rows.", content)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class JsonRowsNormalizerTechnique(BaseTechnique):
    """Normalize JSON objects/arrays into row dictionaries for downstream storage."""

    technique_id = "scraping.parser.json_rows_normalizer"
    module_id = M09_MODULE_ID
    display_name = "JSON rows normalizer"
    description = "Normalize supplied JSON or JSONL records into deterministic row dictionaries."
    tool_name = "json"
    recommended_version = "python-stdlib"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["json_content"]
    optional_inputs = ["record_path"]
    expected_evidence = ["extracted_rows", "normalized_json"]
    input_schema = {"json_content": {"type": "string"}, "record_path": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "json_content", "label": "JSON or JSONL content", "type": "textarea"}]
    success_markers = ["extracted_rows"]
    failure_markers = ["invalid_json"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"extracted_rows": "list", "row_count": "int"}
    version_lock_id = "m09_scraping_intelligence/json-rows-normalizer"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        raw = _string_parameter(context.parameters, "json_content")
        rows: list[dict[str, Any]] = []
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                rows = [item if isinstance(item, dict) else {"value": item} for item in parsed]
            elif isinstance(parsed, dict):
                record_path = _string_parameter(context.parameters, "record_path", required=False)
                value: Any = parsed
                for part in [p for p in record_path.split(".") if p]:
                    value = value[part]
                rows = [item if isinstance(item, dict) else {"value": item} for item in value] if isinstance(value, list) else [value if isinstance(value, dict) else {"value": value}]
            else:
                rows = [{"value": parsed}]
        except (json.JSONDecodeError, KeyError, TypeError):
            for line in raw.splitlines():
                if line.strip():
                    item = json.loads(line)
                    rows.append(item if isinstance(item, dict) else {"value": item})
        content = {"extracted_rows": rows, "row_count": len(rows)}
        evidence = _evidence(context, self.technique_id, "json_rows", "JSON content normalized into row records.", content)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class RssAtomParserTechnique(BaseTechnique):
    """Normalize operator-supplied RSS/Atom feed XML into rows."""

    technique_id = "scraping.advanced.rss_atom"
    module_id = M09_MODULE_ID
    display_name = "RSS/Atom feed parser"
    description = "Parse supplied RSS or Atom XML into normalized feed-item rows without network fetches."
    tool_name = "xml.etree.ElementTree"
    recommended_version = "python-stdlib"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["rss_atom_content", "rss_atom_path"]
    expected_evidence = ["extracted_rows", "source_summary", "normalized_json"]
    input_schema = {"rss_atom_content": {"type": "string"}, "rss_atom_path": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "rss_atom_content", "label": "RSS/Atom XML", "type": "textarea"}]
    success_markers = ["extracted_rows"]
    failure_markers = ["invalid_rss_atom"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"extracted_rows": "list", "source_summary": "dict"}
    version_lock_id = "m09_scraping_intelligence/rss-atom-parser"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        raw, source_path = _read_text_parameter(context.parameters, "rss_atom_content", "rss_atom_path")
        rows = _parse_rss_atom(raw)
        content = {"extracted_rows": rows, "source_summary": {"item_count": len(rows), "source_path": source_path}}
        evidence = _evidence(context, self.technique_id, "rss_atom_rows", "RSS/Atom content parsed into normalized rows.", content)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class SqliteTableWriterTechnique(BaseTechnique):
    """Persist normalized rows into an operator-selected SQLite table."""

    technique_id = "scraping.storage.sqlite_table_writer"
    module_id = M09_MODULE_ID
    display_name = "SQLite scraping table writer"
    description = "Create/update a local SQLite table and insert normalized scraping rows."
    tool_name = "SQLite"
    recommended_version = "python-sqlite3"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["table_name", "rows"]
    optional_inputs = ["sqlite_path"]
    expected_evidence = ["sqlite_rows", "sqlite_table_summary", "normalized_json"]
    input_schema = {"table_name": {"type": "string"}, "rows": {"type": "array"}, "sqlite_path": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "table_name", "label": "SQLite table", "type": "text"}]
    success_markers = ["inserted_rows", "sqlite_path"]
    failure_markers = ["invalid_rows", "invalid_table_name"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"sqlite_path": "str", "table_name": "str", "inserted_rows": "int"}
    version_lock_id = "m09_scraping_intelligence/sqlite-table-writer"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        sqlite_path = _workspace_output_path(context.parameters.get("sqlite_path"), _DEFAULT_SQLITE_PATH)
        result = _create_table_and_insert(sqlite_path, _string_parameter(context.parameters, "table_name"), _list_of_dicts(context.parameters, "rows"))
        content = {"sqlite_rows": result, "sqlite_table_summary": result, **result}
        evidence = _evidence(context, self.technique_id, "sqlite_rows", "Rows persisted into local SQLite storage.", content)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class CsvExportTechnique(BaseTechnique):
    """Write supplied rows to a deterministic CSV export file."""

    technique_id = "scraping.export.csv"
    module_id = M09_MODULE_ID
    display_name = "CSV scraping export"
    description = "Export normalized rows to CSV for external tools without invoking X4 at runtime."
    tool_name = "csv"
    recommended_version = "python-stdlib"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["rows"]
    optional_inputs = ["output_path"]
    expected_evidence = ["export_reference", "normalized_json"]
    input_schema = {"rows": {"type": "array"}, "output_path": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "output_path", "label": "CSV output path", "type": "text"}]
    success_markers = ["export_reference"]
    failure_markers = ["invalid_rows"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"export_reference": "dict", "row_count": "int"}
    version_lock_id = "m09_scraping_intelligence/csv-export"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        rows = _list_of_dicts(context.parameters, "rows")
        if not rows:
            raise ContractError("rows must include at least one object.")
        columns = _infer_columns(rows)
        output_path = _workspace_output_path(context.parameters.get("output_path"), Path("storage/workspaces/m09_scraping_intelligence/exports/scraping_export.csv"))
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        content = {"export_reference": {"format": "csv", "path": output_path.as_posix()}, "row_count": len(rows), "columns": columns}
        evidence = _evidence(context, self.technique_id, "export_reference", "Rows exported to CSV.", content)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class JsonExportTechnique(BaseTechnique):
    """Write supplied rows to a JSON export file."""

    technique_id = "scraping.export.json"
    module_id = M09_MODULE_ID
    display_name = "JSON scraping export"
    description = "Export normalized rows to JSON for downstream review and handoff."
    tool_name = "json"
    recommended_version = "python-stdlib"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["rows"]
    optional_inputs = ["output_path"]
    expected_evidence = ["export_reference", "normalized_json"]
    input_schema = {"rows": {"type": "array"}, "output_path": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "output_path", "label": "JSON output path", "type": "text"}]
    success_markers = ["export_reference"]
    failure_markers = ["invalid_rows"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"export_reference": "dict", "row_count": "int"}
    version_lock_id = "m09_scraping_intelligence/json-export"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        rows = _list_of_dicts(context.parameters, "rows")
        output_path = _workspace_output_path(context.parameters.get("output_path"), Path("storage/workspaces/m09_scraping_intelligence/exports/scraping_export.json"))
        output_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        content = {"export_reference": {"format": "json", "path": output_path.as_posix()}, "row_count": len(rows)}
        evidence = _evidence(context, self.technique_id, "export_reference", "Rows exported to JSON.", content)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)

_DEFAULT_QUEUE_PATH = Path("storage/workspaces/m09_scraping_intelligence/work_queue.sqlite3")


def _queue_path(parameters: dict[str, Any]) -> Path:
    return _workspace_output_path(str(parameters.get("queue_path", "")).strip() or None, _DEFAULT_QUEUE_PATH)


def _init_queue_db(queue_path: Path) -> None:
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(queue_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS work_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                domain TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                priority INTEGER NOT NULL DEFAULT 100,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS rate_limits (
                domain TEXT PRIMARY KEY,
                delay_seconds REAL NOT NULL,
                last_request_at REAL,
                updated_at TEXT NOT NULL
            )
            """
        )


def _enqueue_urls(queue_path: Path, urls: list[str], priority: int) -> dict[str, Any]:
    _init_queue_db(queue_path)
    now = utc_now_iso()
    inserted = 0
    duplicates = 0
    with sqlite3.connect(queue_path) as connection:
        for url in urls:
            parsed = urlparse(url)
            try:
                connection.execute(
                    "INSERT INTO work_items (url, domain, status, priority, created_at, updated_at) VALUES (?, ?, 'pending', ?, ?, ?)",
                    (url, parsed.netloc.lower(), priority, now, now),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                duplicates += 1
        total_pending = connection.execute("SELECT COUNT(*) FROM work_items WHERE status = 'pending'").fetchone()[0]
    return {"queue_path": queue_path.as_posix(), "inserted_count": inserted, "duplicate_count": duplicates, "pending_count": int(total_pending)}


def _robots_allowed(robots_txt: str, url: str, user_agent: str) -> bool:
    from urllib.robotparser import RobotFileParser

    parser = RobotFileParser()
    parsed = urlparse(url)
    parser.set_url(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    parser.parse(robots_txt.splitlines())
    return parser.can_fetch(user_agent, url)


def _rate_limit_decisions(queue_path: Path, urls: list[str], delay_seconds: float, now_epoch: float) -> list[dict[str, Any]]:
    _init_queue_db(queue_path)
    decisions = []
    with sqlite3.connect(queue_path) as connection:
        for url in urls:
            domain = urlparse(url).netloc.lower()
            row = connection.execute("SELECT last_request_at, delay_seconds FROM rate_limits WHERE domain = ?", (domain,)).fetchone()
            configured_delay = delay_seconds if row is None else float(row[1])
            last_request_at = None if row is None or row[0] is None else float(row[0])
            wait_seconds = 0.0 if last_request_at is None else max(0.0, configured_delay - (now_epoch - last_request_at))
            allowed = wait_seconds <= 0.0
            if allowed:
                connection.execute(
                    "INSERT INTO rate_limits (domain, delay_seconds, last_request_at, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(domain) DO UPDATE SET delay_seconds = excluded.delay_seconds, last_request_at = excluded.last_request_at, updated_at = excluded.updated_at",
                    (domain, configured_delay, now_epoch, utc_now_iso()),
                )
            decisions.append({"url": url, "domain": domain, "allowed_by_rate_limit": allowed, "wait_seconds": round(wait_seconds, 3), "delay_seconds": configured_delay})
    return decisions


class PersistentWorkQueueEnqueueTechnique(BaseTechnique):
    """Persist scraping work items to a SQLite queue."""

    technique_id = "scraping.queue.persistent_enqueue"
    module_id = M09_MODULE_ID
    display_name = "Persistent scraping queue enqueue"
    description = "Persist normalized scraping URLs into a SQLite-backed work queue; no in-memory-only queue is used."
    tool_name = "internal_sqlite_queue"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "ScrapingWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["urls"]
    optional_inputs = ["queue_path", "priority"]
    expected_evidence = ["queue_path", "inserted_count", "duplicate_count", "pending_count", "normalized_json"]
    input_schema = {"urls": {"type": "array"}, "queue_path": {"type": "string"}, "priority": {"type": "integer"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "urls", "label": "URLs", "type": "textarea"}]
    success_markers = ["queue_path", "pending_count"]
    failure_markers = ["missing_urls", "invalid_queue_path"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"queue_path": "string", "inserted_count": "integer", "pending_count": "integer"}
    version_lock_id = "m09_scraping_intelligence/persistent-work-queue"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        urls = _unique_urls(_string_list_parameter(context.parameters, "urls"))
        if not urls:
            raise ContractError("urls must include at least one http(s) URL.")
        priority = int(context.parameters.get("priority", 100))
        normalized = _enqueue_urls(_queue_path(context.parameters), urls, priority)
        evidence = _evidence(context, self.technique_id, "persistent_queue_enqueue", "Persistent scraping queue enqueue completed.", normalized)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class RobotsRateLimitPolicyTechnique(BaseTechnique):
    """Evaluate supplied URLs against supplied robots.txt content and persistent rate limits."""

    technique_id = "scraping.policy.robots_rate_limit"
    module_id = M09_MODULE_ID
    display_name = "Robots.txt and rate-limit policy"
    description = "Evaluate operator-supplied URLs against robots.txt text and persisted per-domain rate limits before scraping jobs run."
    tool_name = "internal_robots_rate_policy"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "ScrapingWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["urls", "robots_txt"]
    optional_inputs = ["queue_path", "user_agent", "delay_seconds", "now_epoch"]
    expected_evidence = ["policy_decisions", "blocked_urls", "allowed_urls", "normalized_json"]
    input_schema = {"urls": {"type": "array"}, "robots_txt": {"type": "string"}, "delay_seconds": {"type": "number"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "urls", "label": "URLs", "type": "textarea"}, {"name": "robots_txt", "label": "robots.txt", "type": "textarea"}]
    success_markers = ["policy_decisions"]
    failure_markers = ["missing_urls", "missing_robots_txt"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"policy_decisions": "list", "blocked_urls": "list", "allowed_urls": "list"}
    version_lock_id = "m09_scraping_intelligence/robots-rate-limit-policy"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        urls = _unique_urls(_string_list_parameter(context.parameters, "urls"))
        robots_txt = _string_parameter(context.parameters, "robots_txt")
        user_agent = _string_parameter(context.parameters, "user_agent", required=False) or "ojo-de-dios"
        delay_seconds = float(context.parameters.get("delay_seconds", 1.0))
        now_epoch = float(context.parameters.get("now_epoch", 0.0))
        rate_decisions = {item["url"]: item for item in _rate_limit_decisions(_queue_path(context.parameters), urls, delay_seconds, now_epoch)}
        decisions = []
        for url in urls:
            allowed_by_robots = _robots_allowed(robots_txt, url, user_agent)
            rate = rate_decisions[url]
            allowed = allowed_by_robots and bool(rate["allowed_by_rate_limit"])
            decisions.append(rate | {"allowed_by_robots": allowed_by_robots, "allowed": allowed})
        normalized = {
            "policy_decisions": decisions,
            "allowed_urls": [item["url"] for item in decisions if item["allowed"]],
            "blocked_urls": [item["url"] for item in decisions if not item["allowed"]],
            "queue_path": _queue_path(context.parameters).as_posix(),
        }
        evidence = _evidence(context, self.technique_id, "robots_rate_limit_policy", "Robots.txt and rate-limit policy evaluation completed.", normalized)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


def _string_list_parameter(parameters: dict[str, Any], name: str) -> list[str]:
    value = parameters.get(name)
    if isinstance(value, str):
        return [line.strip() for line in value.replace(",", "\n").splitlines() if line.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    raise ContractError(f"{name} must be a list of strings or newline-separated string.")


def _source_configs(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    sources = parameters.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ContractError("sources must be a non-empty list of source objects.")
    normalized: list[dict[str, Any]] = []
    for source in sources:
        if not isinstance(source, dict):
            raise ContractError("sources entries must be objects.")
        name = str(source.get("name") or source.get("url") or "source").strip()
        url = _normalize_url(str(source.get("url") or ""))
        if not url:
            raise ContractError("each source.url must be an http(s) URL.")
        source_type = str(source.get("type") or "auto").lower()
        if source_type not in {"auto", "json", "jsonl", "rss", "atom", "html", "text"}:
            raise ContractError("source.type must be one of auto/json/jsonl/rss/atom/html/text.")
        normalized.append({"name": name, "url": url, "type": source_type, "headers": source.get("headers", {}) if isinstance(source.get("headers", {}), dict) else {}})
    return normalized


def _dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for record in records:
        url = str(record.get("url") or "").strip().lower()
        title = str(record.get("title") or "").strip().lower()
        raw_key = url or json.dumps(record, sort_keys=True, ensure_ascii=False)
        key = hashlib.sha256(f"{raw_key}|{title}".encode("utf-8")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record | {"dedupe_key": key})
    return deduped


def _records_from_json_payload(payload: Any, source: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        candidates = payload.get("items") or payload.get("results") or payload.get("data") or [payload]
    else:
        candidates = payload
    if isinstance(candidates, dict):
        candidates = [candidates]
    if not isinstance(candidates, list):
        return []
    records = []
    for item in candidates:
        if isinstance(item, dict):
            url = item.get("url") or item.get("link") or item.get("href")
            records.append({"source_name": source["name"], "source_url": source["url"], "title": item.get("title") or item.get("name"), "url": _normalize_url(str(url)) if url else None, "published": item.get("published") or item.get("date"), "raw": item})
    return records


def _parse_source_response(source: dict[str, Any], text: str, content_type: str) -> list[dict[str, Any]]:
    source_type = source["type"]
    effective_type = source_type
    if effective_type == "auto":
        lowered = content_type.lower()
        if "json" in lowered:
            effective_type = "jsonl" if "\n" in text.strip() and not text.strip().startswith(("{", "[")) else "json"
        elif "xml" in lowered or "rss" in lowered or "atom" in lowered:
            effective_type = "rss"
        elif "html" in lowered:
            effective_type = "html"
        else:
            effective_type = "text"
    if effective_type in {"rss", "atom"}:
        return [{"source_name": source["name"], "source_url": source["url"], **item} for item in _parse_rss_atom(text)]
    if effective_type == "html":
        return [{"source_name": source["name"], "source_url": source["url"], "url": url, "title": None, "published": None} for url in _extract_urls_from_html(text, source["url"])]
    if effective_type == "jsonl":
        rows = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                rows.extend(_records_from_json_payload(json.loads(line), source))
            except json.JSONDecodeError:
                continue
        return rows
    if effective_type == "json":
        try:
            return _records_from_json_payload(json.loads(text), source)
        except json.JSONDecodeError as error:
            raise ContractError(f"Source {source['name']} returned invalid JSON.") from error
    return [{"source_name": source["name"], "source_url": source["url"], "url": url, "title": None, "published": None} for url in _extract_urls_from_text(text, source["url"])]


class PublicSourceConnectorTechnique(BaseTechnique):
    """Fetch configured public sources and deduplicate discovered records."""

    technique_id = "scraping.connectors.public_sources"
    module_id = M09_MODULE_ID
    display_name = "Public source connectors"
    description = "Fetch operator-configured public JSON/RSS/HTML/text sources and deduplicate records before downstream scraping/AI."
    tool_name = "requests"
    recommended_version = "requests 2.x"
    runtime = "python_lib"
    worker = "ScrapingWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["sources"]
    optional_inputs = ["timeout_seconds", "user_agent", "max_sources"]
    expected_evidence = ["source_results", "deduplicated_records", "normalized_json"]
    input_schema = {"sources": {"type": "array"}, "timeout_seconds": {"type": "integer"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "sources", "label": "Public sources", "type": "textarea"}]
    success_markers = ["deduplicated_records"]
    failure_markers = ["missing_sources", "source_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"source_results": "list", "deduplicated_records": "list"}
    version_lock_id = "m09_scraping_intelligence/public-source-connectors"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        sources = _source_configs(context.parameters)
        timeout = int(context.parameters.get("timeout_seconds", 20))
        user_agent = _string_parameter(context.parameters, "user_agent", required=False) or "ojo-de-dios-m09"
        max_sources = int(context.parameters.get("max_sources", len(sources)))
        source_results = []
        records = []
        for source in sources[:max_sources]:
            headers = {"user-agent": user_agent} | source["headers"]
            response = requests.get(source["url"], headers=headers, timeout=timeout)
            content_type = response.headers.get("content-type", "")
            parsed_records = _parse_source_response(source, response.text, content_type)
            source_results.append({"source_name": source["name"], "source_url": source["url"], "status_code": response.status_code, "record_count": len(parsed_records), "content_type": content_type})
            if response.status_code >= 400:
                continue
            records.extend(record for record in parsed_records if record.get("url") or record.get("title"))
        deduped = _dedupe_records(records)
        normalized = {"source_results": source_results, "deduplicated_records": deduped, "record_count": len(deduped), "duplicate_count": max(0, len(records) - len(deduped))}
        evidence = _evidence(context, self.technique_id, "public_source_connector_results", "Public source connectors fetched and deduplicated records.", normalized)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)
