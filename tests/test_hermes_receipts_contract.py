"""Hermes assist receipt persistence contract tests."""

from pathlib import Path

from app.ai.hermes_assist import HermesAssistRequest, HermesAssistResponse
from app.ai.hermes_receipts import (
    list_hermes_assist_receipts,
    read_hermes_assist_receipt,
    redact_hermes_payload,
    write_hermes_assist_receipt,
)


def test_redact_hermes_payload_removes_secret_keys_and_inline_assignments() -> None:
    payload = {
        "api_key": "secret-value",
        "nested": {"token": "hidden", "note": "password=abc123"},
        "safe": "value",
    }

    redacted = redact_hermes_payload(payload)

    assert redacted["api_key"] == "<redacted>"
    assert redacted["nested"]["token"] == "<redacted>"
    assert redacted["nested"]["note"] == "password=<redacted>"
    assert redacted["safe"] == "value"


def test_write_read_and_list_hermes_receipts_roundtrip_redacted_payload(tmp_path: Path) -> None:
    request = HermesAssistRequest(
        question="Review this safely with token=abc123",
        context={"module_id": "m16_ops_quality", "api_key": "secret-value"},
    )
    response = HermesAssistResponse(
        model="deepseek-v4-flash",
        content='{"answer":"ok","password":"abc123"}',
        raw={"id": "chat-test", "authorization": "Bearer secret"},
    )

    persisted = write_hermes_assist_receipt(request, response, receipt_id="receipt-1", repo_root=tmp_path)
    recovered = read_hermes_assist_receipt("receipt-1", repo_root=tmp_path)
    receipts = list_hermes_assist_receipts(repo_root=tmp_path)

    assert persisted.path.is_file()
    assert persisted.sha256 == recovered.sha256
    assert persisted.byte_count == recovered.byte_count
    assert [item.receipt_id for item in receipts] == ["receipt-1"]
    assert recovered.payload["request"]["context"]["api_key"] == "<redacted>"
    assert recovered.payload["request"]["question"] == "Review this safely with token=<redacted>"
    assert recovered.payload["response"]["raw"]["authorization"] == "<redacted>"
    receipt_text = recovered.path.read_text(encoding="utf-8")
    assert "secret-value" not in receipt_text
    assert "abc123" not in receipt_text
